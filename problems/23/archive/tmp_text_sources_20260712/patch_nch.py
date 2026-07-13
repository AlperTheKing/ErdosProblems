from pathlib import Path
p = Path('problems/23/writeup/_codex_nch_sanity_gate.py')
lines = p.read_text().splitlines()
out = []
i = 0
while i < len(lines):
    line = lines[i]
    if line.strip() == '"th_violations": [],':
        out.append(line)
        if i + 1 < len(lines) and 'terminal_hall_checked' not in lines[i + 1]:
            out.append('        "terminal_hall_checked": 0,')
            out.append('        "terminal_hall_skipped": 0,')
        i += 1
        continue
    if 'if hall.get("checked") and hall["violations"]' in line:
        out.append('                    if hall.get("checked"):')
        out.append('                        rec["terminal_hall_checked"] += 1')
        out.append('                        if hall["violations"] and len(rec["th_violations"]) < 5:')
        out.append('                            rec["th_violations"].append({')
        out.append('                                "side": cut_rec["side"],')
        out.append('                                "T": list(terminals),')
        out.append('                                "hall": hall,')
        out.append('                            })')
        out.append('                    else:')
        out.append('                        rec["terminal_hall_skipped"] += 1')
        i += 6
        continue
    if '`n            f"TH_skipped=' in line:
        a, b = line.split('`n')
        out.append(a)
        out.append(b)
        i += 1
        continue
    out.append(line)
    i += 1
p.write_text('\n'.join(out) + '\n')
