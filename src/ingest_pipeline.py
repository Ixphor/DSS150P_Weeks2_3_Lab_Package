from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil, csv, uuid
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
RAW = ROOT / 'raw'
STATE = ROOT / 'state'
OUTPUTS = ROOT / 'outputs'
API_URL = 'http://127.0.0.1:8000/api/events'
LOG_FILE = OUTPUTS / 'pipeline_run_log.csv'

def utc_now(): return datetime.now(timezone.utc).isoformat()

def sha256_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def load_watermark():
    p = STATE / 'api_watermark.json'
    if not p.exists(): return None
    return json.loads(p.read_text())['updated_at']

def save_watermark(value):
    STATE.mkdir(exist_ok=True)
    (STATE / 'api_watermark.json').write_text(json.dumps({'updated_at': value}, indent=2))

def write_log(run_id, start_t, end_t, status, source, read_c, write_c, dupes, wm_before, wm_after, err):
    OUTPUTS.mkdir(exist_ok=True)
    write_header = not LOG_FILE.exists()
    with LOG_FILE.open('a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['run_id', 'started_at', 'finished_at', 'status', 'source', 'records_read', 'records_written', 'duplicates_removed', 'watermark_before', 'watermark_after', 'error_message'])
        writer.writerow([run_id, start_t, end_t, status, source, read_c, write_c, dupes, wm_before, wm_after, err])

def ingest_files():
    print("Files")
    run_id = str(uuid.uuid4())
    start_t = utc_now()
    raw_files_dir = RAW / 'files'
    raw_files_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = raw_files_dir / 'manifest.json'
    
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    sources = ['customers.csv', 'orders.json', 'products.parquet']
    
    for filename in sources:
        src_path = DATA / filename
        if not src_path.exists():
            print(f"{filename} missing")
            write_log(run_id, start_t, utc_now(), 'Failed', filename, 0, 0, 0, '', '', 'File missing')
            continue
            
        file_hash = sha256_file(src_path)
        if filename in manifest and manifest[filename]['sha256'] == file_hash:
            print(f"{filename} skipped")
            write_log(run_id, start_t, utc_now(), 'Skipped', filename, 0, 0, 0, '', '', '')
            continue
            
        shutil.copy2(src_path, raw_files_dir / filename)
        manifest[filename] = {"source_file": filename, "ingested_at": utc_now(), "sha256": file_hash, "bytes": src_path.stat().st_size}
        print(f"{filename} done")
        write_log(run_id, start_t, utc_now(), 'Success', filename, 1, 1, 0, '', '', '')
        
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print("Files done")

def fetch_api_page(page, per_page=20, updated_after=None):
    params = {'page': page, 'per_page': per_page}
    if updated_after: params['updated_after'] = updated_after
    r = requests.get(API_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def ingest_api():
    print("API")
    run_id = str(uuid.uuid4())
    start_t = utc_now()
    watermark = load_watermark()
    print(f"WM: {watermark}")
    
    page = 1
    has_more = True
    raw_records = []
    
    try:
        while has_more:
            print(f"Page {page}")
            data = fetch_api_page(page=page, per_page=50, updated_after=watermark)
            now = utc_now()
            for item in data.get('items', []):
                item['_ingested_at'] = now
                item['_source'] = 'REST API'
                raw_records.append(item)
            has_more = data.get('has_more', False)
            page += 1
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        write_log(run_id, start_t, utc_now(), 'Failed', 'REST API', len(raw_records), 0, 0, watermark, watermark, str(e))
        return
        
    if not raw_records:
        print("No records")
        print("API done")
        write_log(run_id, start_t, utc_now(), 'Success', 'REST API', 0, 0, 0, watermark, watermark, '')
        return
        
    deduped = {}
    for r in raw_records:
        eid = r['event_id']
        if eid not in deduped or r['updated_at'] > deduped[eid]['updated_at']:
            deduped[eid] = r
            
    final_records = list(deduped.values())
    dupes = len(raw_records) - len(final_records)
    print(f"Raw: {len(raw_records)}, Dupes: {dupes}")
    
    api_dir = RAW / 'api'
    api_dir.mkdir(parents=True, exist_ok=True)
    temp_file = api_dir / 'events_temp.jsonl'
    final_file = api_dir / 'events.jsonl'
    
    if final_file.exists(): shutil.copy2(final_file, temp_file)
    with temp_file.open('a' if final_file.exists() else 'w', encoding='utf-8') as f:
        for r in final_records: f.write(json.dumps(r) + '\n')
    temp_file.replace(final_file)
    print("Wrote API")
    
    max_updated_at = max(r['updated_at'] for r in final_records)
    new_wm = watermark
    if watermark is None or max_updated_at > watermark:
        save_watermark(max_updated_at)
        new_wm = max_updated_at
        print(f"New WM: {new_wm}")
        
    write_log(run_id, start_t, utc_now(), 'Success', 'REST API', len(raw_records), len(final_records), dupes, watermark, new_wm, '')
    print("API done")

if __name__ == '__main__':
    RAW.mkdir(exist_ok=True)
    STATE.mkdir(exist_ok=True)
    ingest_files()
    ingest_api()