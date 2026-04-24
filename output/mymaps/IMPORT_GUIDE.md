# Google My Maps Import Guide

## Map Title
- `2026 Milano Honeymoon`

## Layer Import Order
1. `00_base_transport.csv`
2. `01_day1_arrival.csv`
3. `02_day2_milan_core.csv`
4. `03_day3_birthday_shopping.csv`
5. `04_day4_como.csv`
6. `05_day5_bergamo.csv`
7. `06_day6_departure.csv`
8. `07_backup_routes.csv`

## Import Mapping
- Location column: `query`
- Title column: `name`

## Style By
- Group places by column: `category_ko`

## Category Colors
- `호텔`: blue
- `교통`: gray
- `공항`: gray
- `랜드마크`: yellow
- `식음`: red
- `쇼핑`: pink
- `박물관`: purple
- `건축`: purple
- `공원`: green
- `지역`: orange
- `당일치기`: teal

## Reimport Rule
- Reimport matching column: `place_key`
