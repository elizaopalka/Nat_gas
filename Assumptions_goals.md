All assumptions calculations and steps to the hedging jet fuel project:

Calculations + Assumptions that the project will be based upon:

Future spot price = Current diesel price × (1 + Scenario price change)
Budget Cost = Gallons × Budget fuel price
No hedge cost = Gallons × Future spot price
Fixed price cost = Gallons × Supplier fixed price
Savings versus No hedge = No hedge cost - Strategy cost



For the hedge ration the calculations that are going to be used are:

Futures net cost = Unhedged cost
                   - Gallons × h × (Future spot price - Futures price)

Call option net cost = Unhedged cost
                       - Gallons × h × max(Future spot price - Call strike, 0)
                       + Gallons × h × Call premium

Collar net cost = Unhedged cost
                  - Gallons × h × max(Future spot price - Call strike, 0)
                  + Gallons × h × max(Put strike - Future spot price, 0)
                  + Gallons × h × (Call premium - Put premium)


STEPS:

1. Process data and draw a curve at one point in time with futures prices against maturity 
2. How the curve changes over the time (from backwardation to contango an back again)
3. How spot prices of jet fuel establish how the NG futures can hedge the risk over time periods
4. Implement a Monte Carlo simulation to establish during which specific moments the Jet Fuel prices will change the most 
5. Specific case of hedging jet fuel and its consequences 
6. Scenario-based code for further use 

ARTICLES & SOURCES USED:

https://pmc.ncbi.nlm.nih.gov/articles/PMC7147842/
