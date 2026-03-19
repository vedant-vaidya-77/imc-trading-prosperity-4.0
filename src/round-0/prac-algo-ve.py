from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import json

class Trader:
    
    def run(self, state: TradingState):
        result = {}
        
        # 1. STATE MANAGEMENT
        if state.traderData == "":
            tomato_history = []
        else:
            tomato_history = json.loads(state.traderData)

        # 2. PROCESS EACH PRODUCT
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            # We need the current order book extremes for BOTH products now to Penny-Jump
            if len(order_depth.buy_orders) > 0 and len(order_depth.sell_orders) > 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_bid + best_ask) / 2
                
                # ---------------------------------------------------------
                # STRATEGY 1: EMERALDS (Penny-Jumping Market Maker)
                # ---------------------------------------------------------
                if product == 'EMERALDS':
                    current_position = state.position.get('EMERALDS', 0)
                    POSITION_LIMIT = 20
                    
                    # We know fair value is 10000. 
                    # Instead of a passive 9998/10002, we aggressively jump the queue.
                    # We will bid 1 point higher than the best bid, up to a max of 9999.
                    my_buy_price = min(best_bid + 1, 9999)
                    # We will ask 1 point lower than the best ask, down to a min of 10001.
                    my_sell_price = max(best_ask - 1, 10001)
                    
                    max_buy = POSITION_LIMIT - current_position
                    if max_buy > 0:
                        orders.append(Order(product, my_buy_price, max_buy))
                        
                    max_sell = -POSITION_LIMIT - current_position
                    if max_sell < 0:
                        orders.append(Order(product, my_sell_price, max_sell))
                        
                    result[product] = orders

                # ---------------------------------------------------------
                # STRATEGY 2: TOMATOES (Dynamic Penny-Jumping)
                # ---------------------------------------------------------
                if product == 'TOMATOES':
                    current_position = state.position.get('TOMATOES', 0)
                    POSITION_LIMIT = 20
                    
                    tomato_history.append(mid_price)
                    
                    if len(tomato_history) > 5:
                        tomato_history.pop(0)
                        
                    if len(tomato_history) == 5:
                        # 1. Calculate Fair Value
                        sma = sum(tomato_history) / 5
                        
                        buy_vol = sum(order_depth.buy_orders.values())
                        sell_vol = abs(sum(order_depth.sell_orders.values())) 
                        total_vol = buy_vol + sell_vol
                        
                        obi = 0
                        if total_vol > 0:
                            obi = (buy_vol - sell_vol) / total_vol 
                            
                        obi_shift = 0
                        if obi > 0.5:
                            obi_shift = 1   
                        elif obi < -0.5:
                            obi_shift = -1  
                            
                        dynamic_fair_value = sma + obi_shift
                        skew = -int(current_position / 10)
                        
                        # 2. AGGRESSIVE PENNY-JUMPING EXECUTION
                        # We want to be at the very front of the line (best_bid + 1),
                        # BUT we refuse to pay more than our (dynamic_fair_value - 1 + skew).
                        my_buy_price = min(best_bid + 1, int(round(dynamic_fair_value - 1 + skew)))
                        
                        # We want to sell faster than anyone else (best_ask - 1),
                        # BUT we refuse to sell for less than our (dynamic_fair_value + 1 + skew).
                        my_sell_price = max(best_ask - 1, int(round(dynamic_fair_value + 1 + skew)))
                        
                        max_buy = POSITION_LIMIT - current_position
                        if max_buy > 0:
                            orders.append(Order(product, my_buy_price, max_buy))
                            
                        max_sell = -POSITION_LIMIT - current_position
                        if max_sell < 0:
                            orders.append(Order(product, my_sell_price, max_sell))

                    result[product] = orders

        new_traderData = json.dumps(tomato_history)
        return result, 1, new_traderData