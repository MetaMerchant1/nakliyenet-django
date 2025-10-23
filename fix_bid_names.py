#!/usr/bin/env python
"""
Fix empty carrier names in existing bids
Run this script once to update all bids with empty carrier_name
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nakliyenet.settings')
django.setup()

from website.models import Bid

def fix_carrier_names():
    """Update all bids with empty carrier names"""
    bids_without_name = Bid.objects.filter(carrier_name='')

    print(f"Found {bids_without_name.count()} bids with empty carrier_name")

    updated_count = 0
    for bid in bids_without_name:
        try:
            # Get carrier user
            carrier_user = bid.carrier.user

            # Determine name with fallback
            carrier_name = (
                carrier_user.get_full_name() or
                carrier_user.username or
                carrier_user.email.split('@')[0] or
                'Taşıyıcı'
            )

            # Update bid
            bid.carrier_name = carrier_name
            bid.save(update_fields=['carrier_name'])

            print(f"✓ Updated bid {bid.bid_id}: {carrier_name}")
            updated_count += 1

        except Exception as e:
            print(f"✗ Error updating bid {bid.bid_id}: {e}")

    print(f"\n✅ Updated {updated_count} bids successfully!")

if __name__ == '__main__':
    fix_carrier_names()
