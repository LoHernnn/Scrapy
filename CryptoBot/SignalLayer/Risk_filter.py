# Risk Filters (garde-fous obligatoires)
#Empêcher l’algo de se suicider.
#IF daily_loss > 2% → STOP TRADING
#IF global_dd > 10% → KILL SWITCH
#IF already exposed to BTC AND new trade correlated > 0.8 → BLOCK
#IF major_event_soon → NO TRADE
#MAX_TRADES_PER_DAY = 5
#MIN_TIME_BETWEEN_TRADES = 30min
#Donnée	Utilité
#Correlation	Exposition
#Open interest	Crowded trade
