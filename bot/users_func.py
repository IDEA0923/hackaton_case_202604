import database

async def registration(user_id : int , role : int)-> int: # []
    if await is_regged(user_id=user_id):
        return 1 #already regged 
    try:
        await database.db.awrite(f"INSERT INTO users (id, role) VALUES ({user_id} , {role})")
        return 0
    except:
        return 2
    

async def is_regged(user_id : int)->bool:
    response  = await database.db.aread(f"SELECT * FROM users WHERE id = {user_id}")
    print(str(response))
    return response != []

async def get_role(user_id : int)->int:
    return int((await database.db.aread(f"SELECT * FROM users WHERE id = {user_id}"))[0][1])