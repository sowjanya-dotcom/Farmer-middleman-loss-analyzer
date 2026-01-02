import csv
from dataclasses import dataclass
from typing import List


@dataclass
class CropRecord:
    crop: str
    quantity_kg: float
    farm_gate_price_per_kg: float
    market_price_per_kg: float
    transport_cost_per_kg: float
    storage_loss_percent: float


def load_csv(path: str) -> List[CropRecord]:
    records: List[CropRecord] = []
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            records.append(CropRecord(
                crop=r['crop'],
                quantity_kg=float(r['quantity_kg']),
                farm_gate_price_per_kg=float(r['farm_gate_price_per_kg']),
                market_price_per_kg=float(r['market_price_per_kg']),
                transport_cost_per_kg=float(r['transport_cost_per_kg']),
                storage_loss_percent=float(r['storage_loss_percent'])
            ))
    return records


def analyze_record(rec: CropRecord) -> dict:
    """Compute loss for a single crop record.

    Interpretation used:
    - If farmer could sell at market and bear transport+storage loss, their net would be:
      net_market = market_price * qty - transport_cost*qty - storage_loss_value
    - Actual revenue at farm-gate = farm_gate_price * qty
    - Loss = net_market - actual_revenue (only positive losses shown)

    Returns a dict with computed fields.
    """
    qty = rec.quantity_kg
    market_value = rec.market_price_per_kg * qty
    transport_cost_value = rec.transport_cost_per_kg * qty
    storage_loss_value = (rec.storage_loss_percent / 100.0) * market_value

    net_if_sold_at_market = market_value - transport_cost_value - storage_loss_value
    actual_revenue = rec.farm_gate_price_per_kg * qty
    loss = net_if_sold_at_market - actual_revenue
    loss = round(loss, 2)

    return {
        'crop': rec.crop,
        'quantity_kg': qty,
        'farm_gate_total': round(actual_revenue, 2),
        'market_net_total': round(net_if_sold_at_market, 2),
        'loss': max(loss, 0.0)
    }


def analyze_all(records: List[CropRecord]) -> dict:
    rows = [analyze_record(r) for r in records]
    total_loss = round(sum(r['loss'] for r in rows), 2)
    return {'rows': rows, 'total_loss': total_loss}


if __name__ == '__main__':
    recs = load_csv('sample_data.csv')
    out = analyze_all(recs)
    print('Total estimated loss: ₹', out['total_loss'])
    for r in out['rows']:
        print(r)
