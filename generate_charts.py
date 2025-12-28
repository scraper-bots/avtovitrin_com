import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for professional charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('car_listings_final_complete.csv')

# Data Cleaning
print("Cleaning data...")
# Remove rows with missing critical data (brand, model, price)
df_clean = df[df['brand'].notna() & df['model'].notna() & df['price'].notna()].copy()

# Clean price column - extract numeric values
df_clean['price_numeric'] = df_clean['price'].str.extract('(\d+)').astype(float)

# Clean mileage column - extract numeric values
df_clean['mileage_numeric'] = df_clean['mileage'].str.replace(' ', '').str.extract('(\d+)').astype(float)

# Clean engine volume
df_clean['engine_volume_numeric'] = df_clean['engine_volume'].str.extract('(\d+\.?\d*)').astype(float)

# Clean views
df_clean['views_numeric'] = pd.to_numeric(df_clean['views'], errors='coerce')

# Filter out unrealistic data
df_clean = df_clean[df_clean['price_numeric'] > 1000]  # Minimum realistic price
df_clean = df_clean[df_clean['price_numeric'] < 500000]  # Maximum realistic price

print(f"Total valid listings: {len(df_clean)}")

# Create output directory
import os
os.makedirs('charts', exist_ok=True)

# ============================================================================
# CHART 1: Top 15 Car Brands by Average Price
# ============================================================================
print("Generating Chart 1: Brand Performance by Average Price...")
brand_stats = df_clean.groupby('brand').agg({
    'price_numeric': ['mean', 'count']
}).round(0)
brand_stats.columns = ['avg_price', 'count']
brand_stats = brand_stats[brand_stats['count'] >= 1].sort_values('avg_price', ascending=False).head(15)

plt.figure(figsize=(12, 6))
colors = sns.color_palette("viridis", len(brand_stats))
bars = plt.barh(range(len(brand_stats)), brand_stats['avg_price'], color=colors)
plt.yticks(range(len(brand_stats)), brand_stats.index)
plt.xlabel('Average Price (AZN)', fontsize=12, fontweight='bold')
plt.title('Top 15 Premium Brands by Average Listing Price', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add value labels
for i, (idx, row) in enumerate(brand_stats.iterrows()):
    plt.text(row['avg_price'] + 1000, i, f"{int(row['avg_price']):,} AZN",
             va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/01_brand_average_price.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 2: Market Distribution by Body Type
# ============================================================================
print("Generating Chart 2: Market Distribution by Body Type...")
body_type_dist = df_clean['body_type'].value_counts().head(10)

plt.figure(figsize=(12, 6))
colors = sns.color_palette("Set2", len(body_type_dist))
bars = plt.bar(range(len(body_type_dist)), body_type_dist.values, color=colors)
plt.xticks(range(len(body_type_dist)), body_type_dist.index, rotation=45, ha='right')
plt.ylabel('Number of Listings', fontsize=12, fontweight='bold')
plt.title('Inventory Distribution by Vehicle Body Type', fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, v in enumerate(body_type_dist.values):
    plt.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/02_body_type_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 3: Price Distribution by Transmission Type
# ============================================================================
print("Generating Chart 3: Price Analysis by Transmission...")
trans_price = df_clean.groupby('transmission')['price_numeric'].agg(['mean', 'count']).round(0)
trans_price = trans_price[trans_price['count'] >= 3].sort_values('mean', ascending=False)

plt.figure(figsize=(10, 6))
colors = ['#2ecc71' if x == trans_price['mean'].max() else '#3498db' for x in trans_price['mean']]
bars = plt.bar(range(len(trans_price)), trans_price['mean'], color=colors)
plt.xticks(range(len(trans_price)), trans_price.index, rotation=0)
plt.ylabel('Average Price (AZN)', fontsize=12, fontweight='bold')
plt.title('Average Vehicle Price by Transmission Type', fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, v in enumerate(trans_price['mean']):
    plt.text(i, v + 500, f"{int(v):,}", ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/03_price_by_transmission.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 4: Fuel Type Market Share and Pricing
# ============================================================================
print("Generating Chart 4: Fuel Type Analysis...")
fuel_stats = df_clean.groupby('fuel_type').agg({
    'price_numeric': 'mean',
    'listing_id': 'count'
}).round(0)
fuel_stats.columns = ['avg_price', 'count']
fuel_stats = fuel_stats[fuel_stats['count'] >= 2].sort_values('count', ascending=False)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Market share
colors1 = sns.color_palette("pastel", len(fuel_stats))
ax1.bar(range(len(fuel_stats)), fuel_stats['count'], color=colors1)
ax1.set_xticks(range(len(fuel_stats)))
ax1.set_xticklabels(fuel_stats.index, rotation=45, ha='right')
ax1.set_ylabel('Number of Listings', fontweight='bold')
ax1.set_title('Market Share by Fuel Type', fontweight='bold', fontsize=12)
for i, v in enumerate(fuel_stats['count']):
    ax1.text(i, v + 0.5, str(int(v)), ha='center', va='bottom', fontweight='bold')

# Average price
colors2 = sns.color_palette("muted", len(fuel_stats))
ax2.bar(range(len(fuel_stats)), fuel_stats['avg_price'], color=colors2)
ax2.set_xticks(range(len(fuel_stats)))
ax2.set_xticklabels(fuel_stats.index, rotation=45, ha='right')
ax2.set_ylabel('Average Price (AZN)', fontweight='bold')
ax2.set_title('Average Price by Fuel Type', fontweight='bold', fontsize=12)
for i, v in enumerate(fuel_stats['avg_price']):
    ax2.text(i, v + 500, f"{int(v):,}", ha='center', va='bottom', fontweight='bold')

plt.suptitle('Fuel Type: Market Dynamics', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('charts/04_fuel_type_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 5: Year vs Price Trend
# ============================================================================
print("Generating Chart 5: Vehicle Age Impact on Pricing...")
year_price = df_clean.groupby('year')['price_numeric'].agg(['mean', 'count']).reset_index()
year_price = year_price[year_price['count'] >= 2].sort_values('year')

plt.figure(figsize=(14, 6))
plt.plot(year_price['year'], year_price['mean'], marker='o', linewidth=2.5,
         markersize=8, color='#e74c3c')
plt.fill_between(year_price['year'], year_price['mean'], alpha=0.3, color='#e74c3c')
plt.xlabel('Manufacturing Year', fontsize=12, fontweight='bold')
plt.ylabel('Average Listing Price (AZN)', fontsize=12, fontweight='bold')
plt.title('Vehicle Depreciation Curve: Price vs Manufacturing Year', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('charts/05_year_price_trend.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 6: Top Cities by Inventory Volume
# ============================================================================
print("Generating Chart 6: Geographic Distribution...")
city_dist = df_clean['city'].value_counts().head(10)

plt.figure(figsize=(12, 6))
colors = sns.color_palette("coolwarm", len(city_dist))
bars = plt.barh(range(len(city_dist)), city_dist.values, color=colors)
plt.yticks(range(len(city_dist)), city_dist.index)
plt.xlabel('Number of Listings', fontsize=12, fontweight='bold')
plt.title('Top 10 Markets by Listing Volume', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add value labels
for i, v in enumerate(city_dist.values):
    plt.text(v + 0.5, i, str(v), va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/06_city_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 7: Credit vs Non-Credit Availability Impact
# ============================================================================
print("Generating Chart 7: Credit Offering Analysis...")
credit_available = df_clean[df_clean['credit_available'].notna()]
credit_stats = credit_available.groupby('credit_available').agg({
    'price_numeric': 'mean',
    'listing_id': 'count'
}).round(0)
credit_stats.columns = ['avg_price', 'count']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Count comparison
colors1 = ['#27ae60', '#e67e22']
ax1.bar(range(len(credit_stats)), credit_stats['count'], color=colors1)
ax1.set_xticks(range(len(credit_stats)))
ax1.set_xticklabels(credit_stats.index, rotation=0)
ax1.set_ylabel('Number of Listings', fontweight='bold')
ax1.set_title('Listings by Credit Availability', fontweight='bold', fontsize=12)
for i, v in enumerate(credit_stats['count']):
    ax1.text(i, v + 0.5, str(int(v)), ha='center', va='bottom', fontweight='bold')

# Price comparison
ax2.bar(range(len(credit_stats)), credit_stats['avg_price'], color=colors1)
ax2.set_xticks(range(len(credit_stats)))
ax2.set_xticklabels(credit_stats.index, rotation=0)
ax2.set_ylabel('Average Price (AZN)', fontweight='bold')
ax2.set_title('Average Price by Credit Availability', fontweight='bold', fontsize=12)
for i, v in enumerate(credit_stats['avg_price']):
    ax2.text(i, v + 500, f"{int(v):,}", ha='center', va='bottom', fontweight='bold')

plt.suptitle('Credit Offering Impact on Market', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('charts/07_credit_availability.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 8: Barter vs No-Barter Listings
# ============================================================================
print("Generating Chart 8: Barter Negotiation Analysis...")
barter_available = df_clean[df_clean['barter_possible'].notna()]
barter_stats = barter_available.groupby('barter_possible').agg({
    'price_numeric': 'mean',
    'listing_id': 'count'
}).round(0)
barter_stats.columns = ['avg_price', 'count']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Count comparison
colors1 = ['#9b59b6', '#16a085']
ax1.bar(range(len(barter_stats)), barter_stats['count'], color=colors1)
ax1.set_xticks(range(len(barter_stats)))
ax1.set_xticklabels(barter_stats.index, rotation=0)
ax1.set_ylabel('Number of Listings', fontweight='bold')
ax1.set_title('Listings by Barter Acceptance', fontweight='bold', fontsize=12)
for i, v in enumerate(barter_stats['count']):
    ax1.text(i, v + 0.5, str(int(v)), ha='center', va='bottom', fontweight='bold')

# Price comparison
ax2.bar(range(len(barter_stats)), barter_stats['avg_price'], color=colors1)
ax2.set_xticks(range(len(barter_stats)))
ax2.set_xticklabels(barter_stats.index, rotation=0)
ax2.set_ylabel('Average Price (AZN)', fontweight='bold')
ax2.set_title('Average Price by Barter Acceptance', fontweight='bold', fontsize=12)
for i, v in enumerate(barter_stats['avg_price']):
    ax2.text(i, v + 500, f"{int(v):,}", ha='center', va='bottom', fontweight='bold')

plt.suptitle('Barter Trading Patterns', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('charts/08_barter_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 9: Drivetrain Type Distribution and Pricing
# ============================================================================
print("Generating Chart 9: Drivetrain Market Analysis...")
drivetrain_stats = df_clean.groupby('drivetrain').agg({
    'price_numeric': 'mean',
    'listing_id': 'count'
}).round(0)
drivetrain_stats.columns = ['avg_price', 'count']
drivetrain_stats = drivetrain_stats[drivetrain_stats['count'] >= 2].sort_values('count', ascending=False)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Market share
colors1 = ['#3498db', '#e74c3c', '#f39c12']
ax1.bar(range(len(drivetrain_stats)), drivetrain_stats['count'], color=colors1)
ax1.set_xticks(range(len(drivetrain_stats)))
ax1.set_xticklabels(drivetrain_stats.index, rotation=0)
ax1.set_ylabel('Number of Listings', fontweight='bold')
ax1.set_title('Market Share by Drivetrain', fontweight='bold', fontsize=12)
for i, v in enumerate(drivetrain_stats['count']):
    ax1.text(i, v + 0.5, str(int(v)), ha='center', va='bottom', fontweight='bold')

# Average price
ax2.bar(range(len(drivetrain_stats)), drivetrain_stats['avg_price'], color=colors1)
ax2.set_xticks(range(len(drivetrain_stats)))
ax2.set_xticklabels(drivetrain_stats.index, rotation=0)
ax2.set_ylabel('Average Price (AZN)', fontweight='bold')
ax2.set_title('Average Price by Drivetrain', fontweight='bold', fontsize=12)
for i, v in enumerate(drivetrain_stats['avg_price']):
    ax2.text(i, v + 500, f"{int(v):,}", ha='center', va='bottom', fontweight='bold')

plt.suptitle('Drivetrain Configuration Impact', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('charts/09_drivetrain_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 10: Top 10 Most Popular Models
# ============================================================================
print("Generating Chart 10: Best-Selling Models...")
model_counts = df_clean['model'].value_counts().head(10)

plt.figure(figsize=(12, 6))
colors = sns.color_palette("rocket", len(model_counts))
bars = plt.barh(range(len(model_counts)), model_counts.values, color=colors)
plt.yticks(range(len(model_counts)), model_counts.index)
plt.xlabel('Number of Listings', fontsize=12, fontweight='bold')
plt.title('Top 10 Models by Listing Volume', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add value labels
for i, v in enumerate(model_counts.values):
    plt.text(v + 0.1, i, str(v), va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/10_popular_models.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 11: Mileage vs Price Correlation
# ============================================================================
print("Generating Chart 11: Mileage Impact on Pricing...")
mileage_price = df_clean[df_clean['mileage_numeric'].notna() &
                          (df_clean['mileage_numeric'] < 500000)].copy()

# Create mileage bins
mileage_price['mileage_bin'] = pd.cut(mileage_price['mileage_numeric'],
                                       bins=[0, 50000, 100000, 150000, 200000, 300000, 500000],
                                       labels=['0-50k', '50-100k', '100-150k', '150-200k', '200-300k', '300k+'])

mileage_avg = mileage_price.groupby('mileage_bin')['price_numeric'].agg(['mean', 'count'])
mileage_avg = mileage_avg[mileage_avg['count'] >= 2]

plt.figure(figsize=(12, 6))
colors = sns.color_palette("YlOrRd_r", len(mileage_avg))
bars = plt.bar(range(len(mileage_avg)), mileage_avg['mean'], color=colors)
plt.xticks(range(len(mileage_avg)), mileage_avg.index, rotation=0)
plt.ylabel('Average Price (AZN)', fontsize=12, fontweight='bold')
plt.xlabel('Mileage Range (km)', fontsize=12, fontweight='bold')
plt.title('Price Depreciation by Mileage Segments', fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, v in enumerate(mileage_avg['mean']):
    plt.text(i, v + 500, f"{int(v):,}", ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/11_mileage_price_correlation.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 12: Engagement Analysis (Views Distribution)
# ============================================================================
print("Generating Chart 12: Listing Engagement Analysis...")
views_df = df_clean[df_clean['views_numeric'].notna()].copy()

# Create view bins
views_df['views_bin'] = pd.cut(views_df['views_numeric'],
                               bins=[0, 200, 400, 600, 800, 1000, 2000],
                               labels=['Low\n(0-200)', 'Medium-Low\n(200-400)',
                                      'Medium\n(400-600)', 'Medium-High\n(600-800)',
                                      'High\n(800-1000)', 'Very High\n(1000+)'])

views_dist = views_df['views_bin'].value_counts().sort_index()

plt.figure(figsize=(12, 6))
colors = sns.color_palette("Greens", len(views_dist))
bars = plt.bar(range(len(views_dist)), views_dist.values, color=colors)
plt.xticks(range(len(views_dist)), views_dist.index, rotation=0)
plt.ylabel('Number of Listings', fontsize=12, fontweight='bold')
plt.xlabel('Engagement Level', fontsize=12, fontweight='bold')
plt.title('Listing Engagement Distribution (by Views)', fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, v in enumerate(views_dist.values):
    plt.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/12_engagement_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 13: Color Preference Analysis
# ============================================================================
print("Generating Chart 13: Color Preference Insights...")
color_stats = df_clean.groupby('color').agg({
    'listing_id': 'count',
    'price_numeric': 'mean'
}).round(0)
color_stats.columns = ['count', 'avg_price']
color_stats = color_stats[color_stats['count'] >= 3].sort_values('count', ascending=False).head(10)

plt.figure(figsize=(12, 6))
colors_palette = sns.color_palette("husl", len(color_stats))
bars = plt.barh(range(len(color_stats)), color_stats['count'], color=colors_palette)
plt.yticks(range(len(color_stats)), color_stats.index)
plt.xlabel('Number of Listings', fontsize=12, fontweight='bold')
plt.title('Top 10 Most Popular Vehicle Colors', fontsize=14, fontweight='bold', pad=20)
plt.gca().invert_yaxis()

# Add value labels
for i, v in enumerate(color_stats['count']):
    plt.text(v + 0.5, i, str(int(v)), va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/13_color_preferences.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 14: Price Range Distribution
# ============================================================================
print("Generating Chart 14: Market Segmentation by Price...")
price_bins = pd.cut(df_clean['price_numeric'],
                    bins=[0, 10000, 20000, 30000, 40000, 50000, 100000, 500000],
                    labels=['Budget\n(<10k)', 'Economy\n(10-20k)', 'Mid-Range\n(20-30k)',
                           'Premium\n(30-40k)', 'Luxury\n(40-50k)', 'High-End\n(50-100k)',
                           'Ultra-Luxury\n(100k+)'])

price_dist = price_bins.value_counts().sort_index()

plt.figure(figsize=(14, 6))
colors = sns.color_palette("viridis", len(price_dist))
bars = plt.bar(range(len(price_dist)), price_dist.values, color=colors)
plt.xticks(range(len(price_dist)), price_dist.index, rotation=0)
plt.ylabel('Number of Listings', fontsize=12, fontweight='bold')
plt.xlabel('Price Segment', fontsize=12, fontweight='bold')
plt.title('Market Segmentation: Inventory by Price Range', fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, v in enumerate(price_dist.values):
    plt.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/14_price_range_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 15: New vs Used Car Market
# ============================================================================
print("Generating Chart 15: New vs Used Vehicle Market...")
new_used_stats = df_clean.groupby('is_new').agg({
    'price_numeric': 'mean',
    'listing_id': 'count'
}).round(0)
new_used_stats.columns = ['avg_price', 'count']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Market volume
colors1 = ['#3498db', '#e74c3c']
ax1.bar(range(len(new_used_stats)), new_used_stats['count'], color=colors1)
ax1.set_xticks(range(len(new_used_stats)))
ax1.set_xticklabels(new_used_stats.index, rotation=0)
ax1.set_ylabel('Number of Listings', fontweight='bold')
ax1.set_title('Market Volume: New vs Used', fontweight='bold', fontsize=12)
for i, v in enumerate(new_used_stats['count']):
    ax1.text(i, v + 1, str(int(v)), ha='center', va='bottom', fontweight='bold')

# Price comparison
ax2.bar(range(len(new_used_stats)), new_used_stats['avg_price'], color=colors1)
ax2.set_xticks(range(len(new_used_stats)))
ax2.set_xticklabels(new_used_stats.index, rotation=0)
ax2.set_ylabel('Average Price (AZN)', fontweight='bold')
ax2.set_title('Average Price: New vs Used', fontweight='bold', fontsize=12)
for i, v in enumerate(new_used_stats['avg_price']):
    ax2.text(i, v + 1000, f"{int(v):,}", ha='center', va='bottom', fontweight='bold')

plt.suptitle('New vs Used Vehicle Market Dynamics', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('charts/15_new_vs_used.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n" + "="*70)
print("ANALYSIS COMPLETE!")
print("="*70)
print(f"\n✓ Total listings analyzed: {len(df_clean)}")
print(f"✓ Charts generated: 15")
print(f"✓ Output directory: ./charts/")
print("\nAll visualizations have been saved successfully.")
print("="*70)
