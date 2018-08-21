
mock:
	docker run -it -p 8332:1080 -p 1090:1090 jamesdbloom/mockserver /opt/mockserver/run_mockserver.sh -serverPort 1090 -proxyPort 1080 -proxyRemotePort 8332 -proxyRemoteHost 10.0.1.23 -logLevel INFO
