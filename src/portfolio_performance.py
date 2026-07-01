import matplotlib.pyplot as plt
from calculations import calculate_portfolio_growth

portfolio_growth = calculate_portfolio_growth()

# Plot portfolio growth
plt.figure(figsize=(10, 6))
plt.plot(portfolio_growth)

plt.title("Portfolio Growth")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")

plt.grid(True)

plt.show()