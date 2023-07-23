#!/usr/bin/env python
import argparse
import json
import sqlite3
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Program to generate JSONL files from a LibreTranslate's suggestions.db")
    parser.add_argument(
        "--db",
        type=str,
        nargs=1,
        help="Path to suggestions.db file",
        default='db/suggestions.db'
    )
    parser.add_argument(
        "--clear",
        action='store_true',
        help="Clear suggestions.db after generation",
        default=False
    )
    args = parser.parse_args()

    output_file = str(int(time.time())) + ".jsonl"

    con = sqlite3.connect(args.db, check_same_thread=False)
    cur = con.cursor()

    with open(output_file, 'w', encoding="utf-8") as f:
        for row in cur.execute('SELECT q, s, source, target FROM suggestions WHERE source != "auto" ORDER BY source'):
            q, s, source, target = row
            obj = {
                'q': q,
                's': s,
                'source': source,
                'target': target
            }
            json.dump(obj, f, ensure_ascii=False)
            f.write('\n')

    print("Wrote %s" % output_file)

    if args.clear:
        cur.execute("DELETE FROM suggestions")
        con.commit()
        print("Cleared " + args.db)