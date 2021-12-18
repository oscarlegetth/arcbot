# import os
# import twitchio
# import asyncio
# from twitchio.ext import pubsub
# from dotenv import load_dotenv

# load_dotenv()
# client = twitchio.Client(token=os.environ['PUBSUB_ACCESS_TOKEN'])
# client.pubsub = pubsub.PubSubPool(client)

# def send_message(self, message):
#     chan = self.get_channel("arcreign")
#     loop = asyncio.get_event_loop()
#     loop.create_task(chan.send(message))

# @client.event()
# async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
#     print(f"{event.reward.title}")

# async def main():
#     topics = [
#         pubsub.channel_points(os.environ['PUBSUB_ACCESS_TOKEN'])[int(os.environ['CHANNEL_ID'])]
#     ]
#     await client.pubsub.subscribe_topics(topics)
#     await client.start()

# # client.loop.run_until_complete(main())
# # client.loop.run_forever()
