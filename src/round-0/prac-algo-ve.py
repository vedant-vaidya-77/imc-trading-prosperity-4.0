from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import json

class Trader:
    
    def run(self, state: TradingState):
        """
        Takes all current market data and returns a tuple of:
        (orders_dict, conversions_integer, new_traderData_string)
        """
        result = {}
        
        # 1. LOAD OUR MEMORY (STATE)
        if state.traderData == "":
            tomato_history = []
        else:
            tomato_history = json.loads(state.traderData)

        # 2. LOOP THROUGH ALL PRODUCTS
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            # ---------------------------------------------------------
            # STRATEGY 1: EMERALDS (The Stationary Asset)
            # ---------------------------------------------------------
            if product == 'EMERALDS':
                current_position = state.position.get('EMERALDS', 0)
                POSITION_LIMIT = 20
                
                # Market Making: Hardcoded Fair Value of 10000
                max_buy = POSITION_LIMIT - current_position
                if max_buy > 0:
                    orders.append(Order(product, 9998, max_buy))
                    
                max_sell = -POSITION_LIMIT - current_position
                if max_sell < 0:
                    orders.append(Order(product, 10002, max_sell))
                    
                result[product] = orders

            # ---------------------------------------------------------
            # STRATEGY 2: TOMATOES (The Trending Asset)
            # ---------------------------------------------------------
            if product == 'TOMATOES':
                current_position = state.position.get('TOMATOES', 0)
                POSITION_LIMIT = 20
                
                if len(order_depth.buy_orders) > 0 and len(order_depth.sell_orders) > 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_ask = min(order_depth.sell_orders.keys())
                    mid_price = (best_bid + best_ask) / 2
                    
                    tomato_history.append(mid_price)
                    
                    # Window Size: 5 ticks
                    if len(tomato_history) > 5:
                        tomato_history.pop(0)
                        
                    if len(tomato_history) == 5:
                        # Dynamic Fair Value (Simple Moving Average)
                        sma = sum(tomato_history) / 5
                        
                        # Market Making: Place limit orders around our SMA
                        # We use round() and int() because the engine requires integer prices
                        my_buy_price = int(round(sma - 2))
                        my_sell_price = int(round(sma + 2))
                        
                        max_buy = POSITION_LIMIT - current_position
                        if max_buy > 0:
                            orders.append(Order(product, my_buy_price, max_buy))
                            
                        max_sell = -POSITION_LIMIT - current_position
                        if max_sell < 0:
                            orders.append(Order(product, my_sell_price, max_sell))

                result[product] = orders

        # 3. SAVE OUR MEMORY FOR THE NEXT TICK
        new_traderData = json.dumps(tomato_history)
        
        return result, 1, new_traderData