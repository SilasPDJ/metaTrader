closing_price_sum = 0
with open('data/SPY.csv') as f:
    content = f.readlines()
    for line in content[-200:]:
        print(line)
        tokens = line.split(",")
        close = tokens[4]
        closing_price_sum += float(close)

print(closing_price_sum / 200)