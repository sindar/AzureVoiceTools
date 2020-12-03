import os, requests, time, sys

def read_subscription_key():
    service_region = "northeurope"

    try:
        with open('subscription-'+ service_region + '.key') as key_file:
                subscription_key = key_file.read().rstrip('\n\r')
    except:
        print("Error reading subscription key file!")
        exit(1)

    if subscription_key is None:
        print("Subscription key is empty!")
        exit(1)

    return subscription_key

def get_token(subscription_key):
    fetch_token_url = 'https://northeurope.api.cognitive.microsoft.com/sts/v1.0/issueToken'
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key
    }
    response = requests.post(fetch_token_url, headers=headers)
    access_token = str(response.text)
    print(access_token)
    return access_token

def text_to_speech(sentence, fname):
    subscription_key = read_subscription_key()
    access_token = get_token(subscription_key)

    constructed_url = "https://northeurope.voice.speech.microsoft.com/cognitiveservices/v1?deploymentId=24edc364-4ace-4dbb-9fdd-7934d4ac80dd"
    headers = {
        'Authorization': 'Bearer ' + str(access_token),
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'riff-16khz-16bit-mono-pcm',
        'User-Agent': 'Bender'
    }

    body = "<speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" \
        xmlns:mstts=\"http://www.w3.org/2001/mstts\" \
        xml:lang=\"en-US\"><voice name=\"Bender concat\">"\
        + sentence + "</voice></speak>"   

    response = requests.post(constructed_url, headers=headers, data=body)
    if response.status_code == 200:
        with open('./res_wav/' + fname + '.wav', 'wb') as audio:
            audio.write(response.content)
            print("\nStatus code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")
    else:
        print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")


def main(argv):
    #print ('Argument List:', str(sys.argv))

    with open('txt.done.data','r') as fin:
        lines = fin.readlines()
    for line in lines:
        record = line.split('"')
        fname = record[0].split()[1]
        sentence = record[1]
        if not os.path.exists('./res_wav/' + fname + '.wav'):
            print ("Writing {}.wav with contents {}".format(fname, sentence))
            text_to_speech(sentence, fname)
            time.sleep(2)

if __name__ == "__main__":
   main(sys.argv[1:])