from livekit import AccessToken, VideoGrant

api_key = "APISnXqsykVhufA"
api_secret = "VKMfMaKfF7gSeh7uVcAgsYacxt1mtZTfqIVoVO9G1JUD"
room = "test-room"
identity = "test-user"

token = AccessToken(api_key, api_secret, identity=identity)
token.add_grant(VideoGrant(room_join=True, room=room))
jwt = token.to_jwt()
print("Generated JWT:", jwt)