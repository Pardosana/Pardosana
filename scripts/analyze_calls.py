#!/usr/bin/env python3
"""
SalesEngine V26.1 — 89 Call Analysis
Reproducible pattern analysis of Fathom transcripts against Domino architecture.
"""
import re, json, sys

def analyze(input_path='Dzivie+zvani.md', output_dir='.'):
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()

    positions = [(m.start(), int(m.group(1))) for m in re.finditer(r'VIEW RECORDING - (\d+) mins', data)]
    print(f"Found {len(positions)} calls")

    signals = {
        'D1_FRAME':     [r'saruna.{0,15}(diagnos|saprast, vai)', r'būs īsāka saruna', r'Mums arī ierakstās'],
        'D4_GAP':       [r'starpība', r'cik.{0,5}pietrūkst', r'cik.{0,5}tev vajag'],
        'D5_PAIN':      [r'besī', r'nervi', r'sāp', r'haoss', r'slikti jūti'],
        'D7_COI_$':     [r'€\d+', r'\d+\s*€', r'\d+\s*eiro'],
        'D9_SELFSELL':  [r'no 1 līdz 10', r'skalā', r'cik gatavs'],
        'D10_SAFETY':   [r'garantija', r'kas pierādīs', r'drošības'],
        'D13_PITCH':    [r'mūsu sistēma', r'mēs piedāvā', r'2400', r'3000'],
        'D14_PRICE':    [r'investīcija', r'cena', r'2400', r'3000'],
        'KILL_YOUR':    [r'vai jums ir jautājumi', r'vai tev ir budžet'],
        'CLOSE_INVOICE':[r'rēķin', r'karti'],
        'CLOSE_DATE':   [r'rīt', r'nākamnedēļ', r'piektdien', r'pirmdien', r'ceturtdien'],
        'OBJ_THINK':    [r'jāpadomā'],
        'OBJ_EXPENSIVE':[r'dārgi'],
        'OBJ_SPOUSE':   [r'sievu', r'vīru', r'jākonsult'],
        'OBJ_TRIED':    [r'jau mēģinā', r'jau bija'],
    }

    results = []
    for i, (start, mins) in enumerate(positions):
        end = positions[i+1][0] if i+1 < len(positions) else len(data)
        block = data[start:end]
        before = data[:start]
        lines_before = [l for l in before.strip().split('\n') if l.strip()]
        title = lines_before[-1] if lines_before else f"Call {i+1}"
        
        lauris_wc = other_wc = 0
        current_speaker = None
        for line in block.split('\n'):
            m = re.match(r'@[\d:\.]+\("[^"]+"\) - (.+?)$', line)
            if m:
                current_speaker = m.group(1).strip()
            elif line.strip() and current_speaker:
                words = len(line.split())
                if 'Lauris' in current_speaker or 'Niks' in current_speaker:
                    lauris_wc += words
                else:
                    other_wc += words
        
        total_wc = lauris_wc + other_wc
        lauris_pct = round(lauris_wc/total_wc*100, 1) if total_wc else 0
        
        row = {'idx': i+1, 'title': title[:100], 'duration': mins,
               'total_words': total_wc, 'operator_pct': lauris_pct,
               'client_pct': round(100-lauris_pct, 1)}
        
        block_lower = block.lower()
        for name, pats in signals.items():
            row[name] = sum(len(re.findall(p, block_lower, re.IGNORECASE)) for p in pats)
        
        sc = 0
        if row['operator_pct'] < 50: sc += 2
        if row['D1_FRAME']: sc += 1
        if row['D4_GAP']: sc += 1
        if row['D5_PAIN']: sc += 1
        if row['D7_COI_$'] >= 3: sc += 2
        if row['D9_SELFSELL']: sc += 2
        if row['D10_SAFETY']: sc += 1
        if row['D14_PRICE']: sc += 1
        if row['CLOSE_INVOICE']: sc += 1
        if row['CLOSE_DATE']: sc += 1
        row['score'] = sc
        
        results.append(row)

    with open(f'{output_dir}/calls_full.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Print summary
    durations = [r['duration'] for r in results]
    op_pcts = [r['operator_pct'] for r in results if r['operator_pct'] > 0]
    scores = [r['score'] for r in results]
    print(f"Total {sum(durations)/60:.1f}h · avg {sum(durations)/len(durations):.1f}min · "
          f"avg op% {sum(op_pcts)/len(op_pcts):.1f} · avg score {sum(scores)/len(scores):.1f}/13")
    return results

if __name__ == '__main__':
    inp = sys.argv[1] if len(sys.argv) > 1 else 'Dzivie+zvani.md'
    analyze(inp)
