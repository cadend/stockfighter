#!/usr/local/bin/python

import time

from SecretKeys import SecretKeys

TRADE_API_KEY = SecretKeys.API_KEY
ACCOUNT = "MW69473897"
VENUE = "EMUEX"
TICKER = "CMC"
BASE_URL = "https://api.stockfighter.io/ob/api/venues/"
ORDER_URL = BASE_URL + VENUE + "/stocks/" + TICKER + "/orders"
QUOTE_URL = BASE_URL + VENUE + "/stocks/" + TICKER + "/quote"
AUTH_HEADER = "X-Starfighter-Authorization"
headers = {AUTH_HEADER:TRADE_API_KEY}

total_purchased = 0
avg_best_ask = 0
total_best_ask = 0
open_orders = {}

h = httplib2.Http(".cache")

while True:

	order_body = {
		"account": ACCOUNT,
		"venue": VENUE,
		"stock": TICKER,
		"qty": 250,
		"direction": 'buy',
		"orderType": 'limit',
		"price": 0
	}

	total_best_ask = 0
	avg_best_ask = 0

	i = 0
	while i < 5:
		resp, content = h.request(QUOTE_URL, 'GET');
		json_content = json.loads(content)
		if "ask" in json_content:
			best_ask = json_content["ask"]
			total_best_ask += best_ask
		else:
			print "skipping - no response from quote API"
			continue
		i += 1

	avg_best_ask = total_best_ask / 5

	order_body["price"] = avg_best_ask

	resp, content = h.request(ORDER_URL, "POST", headers=headers, body=json.dumps(order_body))

	order_json = json.loads(content)

	total_purchased += order_json["totalFilled"]

	if order_json["open"] == True:
		open_orders[order_json["id"]] = order_json["totalFilled"]


	for order_id in open_orders.keys():
		resp, content = h.request(ORDER_URL + "/" + str(order_id), 'GET', headers=headers)
		order_status = json.loads(content)
		if order_status["open"] == False:
			total_purchased += 100 - open_orders[order_id]
			del open_orders[order_id]


	print "total purchased shares = " + str(total_purchased)

	if total_purchased >= 100000:
		break