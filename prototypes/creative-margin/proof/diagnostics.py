from decimal import Decimal
from collections import defaultdict
from engine import calculate

def diagnose():
    groups = defaultdict(list)
    for p in calculate()['projects']:
        if p['status'] == 'calculable':
            groups[p['project_type']].append(p)
    result = []
    for name, group in sorted(groups.items()):
        revenue = sum((p['recognised_revenue_eur'] for p in group), Decimal(0))
        cost = sum((p['known_labour_cost_eur'] + p['posted_direct_cost_eur'] for p in group), Decimal(0))
        planned = sum((p['planned_hours'] for p in group), Decimal(0))
        actual = sum((p['recorded_hours'] for p in group), Decimal(0))
        result.append((name, len(group), actual - planned, revenue - cost, cost / Decimal('0.8') - revenue))
    return result

if __name__ == '__main__':
    for row in diagnose():
        print(row)
