#!/usr/local/bin/python

import httplib2
import json

from SecretKeys import SecretKeys

class SFCore:

	def __init__(self, venue, account):
		self.BASE_URL = "https://api.stockfighter.io/ob/api/venues/"
		self.account = account
		self.venue = venue
		self.venue_url = self.BASE_URL + venue + "/stocks"
		self.header = {"X-Starfighter-Authorization":SecretKeys.API_KEY}
		self.http = httplib2.Http(".cache")
		self.position = {}
		self.open_orders = {}

	def heartbeat(self):
		request_url = "https://api.stockfighter.io/ob/api/heartbeat"
		resp, content = self.http.request(request_url, "GET")
		return json.loads(content)

	def venue_heartbeat(self):
		request_url = self.BASE_URL + self.venue + "/heartbeat"
		resp, content = self.http.request(request_url, "GET")
		return json.loads(content)

	def update(self):
		fufilled_orders = []
		for order_id in open_orders.keys():
			old_older_state = open_orders[order_id]
			new_order_state = self.check_order_status(order_id)
			if new_order_state["open"] == False:
				share_delta = old_order_state["total_amount"] - old_older_state["amount_filled"]
				position_change = share_delta if old_older_state["direction"] == "buy" else (share_delta * -1)
				self.position += position_change
				fufilled_orders.append(order_id)
				continue
			if new_order_state["totalFilled"] > old_older_state["amount_filled"]:
				share_delta = new_order_state["totalFilled"] - old_older_state["amount_filled"]
				position_change = share_delta if old_older_state["direction"] == "buy" else (share_delta * -1)
				old_older_state["amount_filled"] += share_delta
				self.position += position_change
		
		for order_id in fufilled_orders:
			del self.open_orders[order_id]				

	def get_position(self, stock):
		return self.position[stock]


	def get_quote(self, stock):
		quote_url = self.BASE_URL + self.venue + "/stocks/" + stock + "/quote"
		resp, content = self.http.request(self.quote_url, 'GET')
		return json.loads(content)

	def get_venue_state(self):
		resp, content = self.http.request(self.venue_url, "GET")
		return json.loads(content)

	def get_stock_book(self, stock):
		book_url = self.BASE_URL + self.venue + "/stocks/" + stock
		resp, content = self.http.request(book_url, "GET")
		return json.loads(content)

	def buy_stock(self, stock, quantity, price, order_type):
		order_url = self.BASE_URL + self.venue + "/stocks/" + stock + "/orders"
		order_json = self.generate_order_json(stock, quantity, price, "buy", order_type)
		resp, content = self.http.request(order_url, "POST", headers=self.header, body=order_json)
		order_response = json.loads(content)
		if stock not in self.position:
			self.position[stock] = 0
		self.position[stock] += order_response["totalFilled"]
		if order_response["open"] == True:
			self.open_orders[order_response["id"] : {direction:"buy", total_amount:quantity, amount_filled:order_response["totalFilled"]}]

		return order_response


	def sell_stock(self, stock, quantity, price, order_type):
		self.validate_sale(stock, quantity)
		order_url = self.BASE_URL + self.venue + "/stocks/" + stock + "/orders"
		order_json = self.generate_order_json(stock, quantity, price, "sell", order_type)
		resp, content = self.http.request(order_url, "POST", headers=self.header, body=order_json)
		order_response = json.loads(content)
		self.position[stock] -= order_response["totalFilled"]
		if order_response["open"] == True:
			self.open_orders[order_response["id"] : {direction:"sell", total_amount:quantity, amount_filled:order_response["totalFilled"]}]

		return order_response

	def check_order_status(self, order_id, stock):
		request_url = self.BASE_URL + self.venue + "/stocks/" + stock + "/orders/" + str(order_id)
		resp, content = self.http.request(request_url, "GET", headers=self.header)
		return json.loads(content)

	def check_all_orders_status(self):
		request_url = self.BASE_URL + self.venue + "/accounts/" + self.account + "/orders"
		resp, content = self.http.request(request_url, "GET", headers=self.header)
		return json.loads(content)

	def check_all_orders_for_stock(self, stock):
		request_url = self.BASE_URL + self.venue + "/accounts/" + self.account + "/stocks/" + stock + "/orders"
		resp, content = self.http.request(request_url, "GET", headers=self.header)
		return json.loads(content)


	def cancel_order(self, order_id, stock):
		cancel_url = self.BASE_URL + self.venue + "/stocks/" + stock + "/orders/" + order_id + "/cancel"
		resp, content = self.http.request(cancel_url, "POST", headers=self.header)
		order_response = json.loads(content)
		if order_response["totalFilled"] > open_orders[[order_id]["amount_filled"]]:
			share_delta = order_response["totalFilled"] - open_orders[order_id]["amount_filled"]
			position_change = share_delta if open_orders[order_id]["direction"] == "buy" else (share_delta * -1)
			self.position[stock] += position_change
		del self.position[stock]

		return order_response

	def validate_sale(self, stock, quantity):
		assert (stock in self.position),"Tried to sell shares you have never purchased"
		if quantity > self.position[stock]:
			print "CANNOT PLACE ORDER"
			print "YOU TRIED TO SELL " + str(quantity) + " SHARES"
			print "YOU ONLY HAVE A POSITION OF " + str(self.position[stock]) + " SHARES"
			raise RuntimeError("Selling more than you own")

	def generate_order_json(self, stock, quantity, price, buy_sell, order_type):
		order_body = {
			"account": self.account,
			"venue": self.venue,
			"stock": stock,
			"qty": quantity,
			"direction": buy_sell,
			"orderType": order_type,
			"price": price
		}

		return json.dumps(order_body)