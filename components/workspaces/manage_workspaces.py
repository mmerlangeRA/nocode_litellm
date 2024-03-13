from nocode_litellm.server.database.client import add_row_to_table


workspace_file_table_name = "file_workspaces"


async def createFileWorkspace(user_id: str, file_id: str,workspace_id: str): 
    createdFileWorkspace =  add_row_to_table(workspace_file_table_name, {user_id,file_id,workspace_id})
    return createdFileWorkspace
