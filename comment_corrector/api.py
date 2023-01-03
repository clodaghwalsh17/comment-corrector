import requests # TODO add requests to requirements.txt

def api_call(): 
    # Header with authentication detail
    token = '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'
    headers = {'Authorization': 'token ' + token}
    # Create an API request 
    url = 'https://api.github.com/repos/clodaghwalsh17/comment-corrector/commits'
    response = requests.get(url, headers=headers)
    print("Status code: ", response.status_code)
    # In a variable, save the API response.
    response_dict = response.json()
    # Evaluate the results.
    print(response_dict)
     #print(response)