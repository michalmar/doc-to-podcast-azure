# https://github.com/Azure-Samples/Cognitive-Speech-TTS/tree/master/doctopodcast
# Description: This script converts a pdf file to a podcast using Azure OpenAI GPT-4-O and Azure TTS

# inspired by: https://github.com/meta-llama/llama-cookbook/tree/main/end-to-end-use-cases/NotebookLlama


import os
from markitdown import MarkItDown

from dotenv import load_dotenv
load_dotenv()


# setuop your AOAI endpoint, key and speech resource etc.
AOAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT')
AOAI_MODEL_NAME = "gpt-4o"
AOAI_API_VERSION = "2024-06-01"
SPEECH_KEY = os.environ.get('SUBSCRIPTION_SPEECH_KEY')
SPEECH_REGION = os.environ.get('SUBSCRIPTION_SPEECH_REGION')

# debud string
print(f"running against AOAI_ENDPOINT: {AOAI_ENDPOINT}")

def printwithtime(*args):
    # show milliseconds
    import datetime
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), *args)

# download file from url
def download(url, filename):
    import requests

    # if url start with http or https
    if not url.startswith("http") or not url.startswith("https"):
        # copy the file
        import shutil
        shutil.copy(url, filename)
        return "application/pdf"
    else:
        response = requests.get(url)
        with open(filename, 'wb') as file:
            file.write(response.content)    

     # return context type
        return response.headers['content-type']

# convert pdf to text
def pdf2text(pdf_file):


    md = MarkItDown()
    result = md.convert(pdf_file)
    # print(result.text_content)
    text = result.text_content

    # import PyPDF2
    # pdf_file = open(pdf_file, 'rb')
    # pdf_reader = PyPDF2.PdfReader(pdf_file)
    # text = ''
    # for page_num in range(len(pdf_reader.pages)):
    #     page = pdf_reader.pages[page_num]
    #     text += "\n" + page.extract_text()

    print("Text extracted from pdf: ", text[0:100])
    return text


def call_aoai(prompt, text):
    from openai import AzureOpenAI

    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    azure_credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(
        azure_credential, "https://cognitiveservices.azure.com/.default"
    )

    client = AzureOpenAI(
        # api_key = AOAI_KEY,  
        azure_ad_token_provider = token_provider,
        api_version = AOAI_API_VERSION,
        azure_endpoint = AOAI_ENDPOINT
        )
    
    generated_podcast_content = ""
    trycount = 3
    while trycount > 0:
        try:
            completion = client.chat.completions.create(
                model=AOAI_MODEL_NAME,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=4096,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)
            
            generated_podcast_content = completion.choices[0].message.content 
            break
        except Exception as e:
            print(e)
            trycount -= 1
            continue
    
    return generated_podcast_content
    
# generate first page image
def GenerateCoverImage(pdf_file, outimg):
    import fitz

    # open the pdf file
    pdf_document = fitz.open(pdf_file)

    # get the first page

    first_page = pdf_document[0]

    # get the image of the first page
    image = first_page.get_pixmap()

    # save the image
    image.save(outimg)

    print("Cover image generated: ", outimg)


# extract ssml from pdf with gpt
def CreatePodcastSsml(text, callback = None):
    
    # voice1 = "cs-CZ-AntoninNeural"
    # voice2 = "cs-CZ-VlastaNeural"

    # voice1 = "en-us-andrew2:DragonHDLatestNeural"
    # voice2 = "en-us-emma2:DragonHDLatestNeural"
    
    voice1 = "de-DE-FlorianMultilingualNeural"
    voice2 = "de-DE-SeraphinaMultilingualNeural"


    # STEP 1: generate basic podcast script
    if callback is not None:
        callback("Generating podcast script - step 1: basic podcast script")
    prompt_script_writer =  f"""
        You are the a world-class podcast writer, you have worked as a ghost writer for Joe Rogan, Lex Fridman, Ben Shapiro, Tim Ferris. 

        We are in an alternate universe where actually you have been writing every line they say and they just stream it into their brains.

        You have won multiple podcast awards for your writing.
        
        Your job is to write word by word, even "umm, hmmm, right" interruptions by the second speaker based on the PDF upload. Keep it extremely engaging, the speakers can get derailed now and then but should discuss the topic. 

        Remember Speaker 2 is new to the topic and the conversation should always have realistic anecdotes and analogies sprinkled throughout. The questions should have real world example follow ups etc

        Speaker 1: Leads the conversation and teaches the speaker 2, gives incredible anecdotes and analogies when explaining. Is a captivating teacher that gives great anecdotes

        Speaker 2: Keeps the conversation on track by asking follow up questions. Gets super excited or confused when asking questions. Is a curious mindset that asks very interesting confirmation questions

        Make sure the tangents speaker 2 provides are quite wild or interesting. 

        Ensure there are interruptions during explanations or there are "hmm" and "umm" injected throughout from the second speaker. 

        It should be a real podcast with every fine nuance documented in as much detail as possible. Welcome the listeners with a super fun overview and keep it really catchy and almost borderline click bait

        The podcast should be in the format of a conversation between two people.   

        Output language MUST be Czech language.

        ALWAYS START YOUR RESPONSE DIRECTLY WITH SPEAKER 1: 
        DO NOT GIVE EPISODE TITLES SEPERATELY, LET SPEAKER 1 TITLE IT IN HER SPEECH
        DO NOT GIVE CHAPTER TITLES
        IT SHOULD STRICTLY BE THE DIALOGUES
        """

    podcasttext = ""
    podcasttext = call_aoai(prompt_script_writer, text)

    # save the podcast text to file
    with open("podcasttext.txt", "w") as file:
        file.write(podcasttext)

    # STEP 2: generate ssml
    if callback is not None:
        callback("Generating podcast script - step 2: ssml")
    prompt_script_rewriter = f"""
        You are an international oscar winnning screenwriter

        You have been working with multiple award winning podcasters.

        Your job is to use the podcast transcript written below to re-write it for an AI Text-To-Speech Pipeline. A very dumb AI had written this so you have to step up for your kind.

        Make it as engaging as possible, Speaker 1 and 2 will be simulated by different voice engines

        Remember Speaker 2 is new to the topic and the conversation should always have realistic anecdotes and analogies sprinkled throughout. The questions should have real world example follow ups etc

        Speaker 1: Leads the conversation and teaches the speaker 2, gives incredible anecdotes and analogies when explaining. Is a captivating teacher that gives great anecdotes

        Speaker 2: Keeps the conversation on track by asking follow up questions. Gets super excited or confused when asking questions. Is a curious mindset that asks very interesting confirmation questions

        Make sure the tangents speaker 2 provides are quite wild or interesting. 

        Ensure there are interruptions during explanations or there are 'hmm' and 'umm' injected throughout from the Speaker 2.

        REMEMBER THIS WITH YOUR HEART
        The TTS Engine for Speaker 1 cannot do 'umms, hmms' well so keep it straight text

        For Speaker 2 use 'umm, hmm' as much, you can also use [sigh] and [laughs]. BUT ONLY THESE OPTIONS FOR EXPRESSIONS

        It should be a real podcast with every fine nuance documented in as much detail as possible. Welcome the listeners with a super fun overview and keep it really catchy and almost borderline click bait

        Please re-write to make it as characteristic as possible

        START YOUR RESPONSE DIRECTLY WITH SPEAKER 1:

        STRICTLY RETURN YOUR RESPONSE AS A LIST OF TUPLES OK? 

        IT WILL START DIRECTLY WITH THE LIST AND END WITH THE LIST NOTHING ELSE

        Output language MUST be Czech language.

        Output into SSML format like below, please don't change voice name.
        Do not include any leading or trailing brackets, or XML tags, etc., before <speak> attrbure. Output just the SSML.

        Example output:
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='en-US'>
        <voice name='{voice1}' type="Speaker 1"><lang xml:lang="cs-CZ">text</lang></voice> 
        <voice name='{voice2}' type="Speaker 2"><lang xml:lang="cs-CZ">text</lang></voice>
        </speak>
        """
    podcasttext_ssml = ""
    podcasttext_ssml = call_aoai(prompt_script_rewriter, podcasttext)
   
    # save the ssml to file
    with open("podcasttext.ssml", "w") as file:
        file.write(podcasttext_ssml)

    # STEP 3: generate ssml with prosody
    if callback is not None:
        callback("Generating podcast script - step 3: ssml with prosody")
    prompt_ssml_enhancer = """
    You are the a world-class podcast writer, you have worked as a ghost writer for Joe Rogan, Lex Fridman, Ben Shapiro, Tim Ferris.
    You are also an expert in the SSML format for Azure TTS. You have won multiple podcast awards for your writing.

    Your job is to take a podcast script in SSML and emphasize the text with the correct SSML tags for Azure TTS.

    Your focus:
    - make sure all text have prosody tag on plus 24%, e.g. <prosody rate="+24.00%">
    - highlight the key points by using the correct SSML tags
    - add pauses for dramatic effect, e.g. <break time="500s"/>
    - make sure podcast word in Czech is pronounced correctly, set <sub alias="podkástu">podcastu</sub>, or <sub alias="podkást">podcast</sub> for example

    Output:
    - the SSML script with the correct SSML tags
    """

    podcasttext_ssml_enhanced = call_aoai(prompt_ssml_enhancer, podcasttext_ssml)

    # save the podcast text to file
    with open("podcasttext-ssml_enhanced.ssml", "w") as file:
        file.write(podcasttext_ssml_enhanced)


    # create ssml
    if callback is not None:
        callback("Creating podcast ssml done.")
    return podcasttext_ssml_enhanced 

# generate audio with Azure TTS HD voices
def GenerateAudio(ssml, outaudio):
    import azure.cognitiveservices.speech as speechsdk
    import os
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)

    # Creates an audio configuration that points to an audio file.
    audio_output = speechsdk.audio.AudioOutputConfig(filename=outaudio)

    # Creates a speech synthesizer using the Azure Speech Service.
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)

    # Synthesizes the received text to speech.
    result = speech_synthesizer.speak_ssml_async(ssml).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesis was successful. Audio was written to '{}'".format(outaudio))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
        print("Did you update the subscription info?")

# generate pod cast workflow
def GeneratePodcast(url, outaudio, callback = None, coverimage = None):    
    temp_pdf = 'temp.pdf'
    if callback is not None:
        callback("Generating podcast from pdf file: " + url)
    printwithtime("Generating podcast from pdf file: ", url)
    # download the file
    print("Downloading file")
    ct = download(url, temp_pdf)
    print("Content type: ", ct)
    if callback is not None:
        callback("Content type: " + ct)

    # if it is pdf
    if ct != "application/pdf":
        # extract text from file
        printwithtime("Extracting text from url as html")
        if callback is not None:
            callback("Extracting text from url as html")
        import requests
        from bs4 import BeautifulSoup

        # add user agent as windows
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        # response = requests.get(url)
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        temp_pdf = ""
        
    else:
        # convert pdf to text
        printwithtime("Converting pdf to text")
        if callback is not None:
            callback("Converting pdf to text")

        text = pdf2text(temp_pdf)

        # generate cover image
        printwithtime("Generating cover image")
        if callback is not None:
            callback("Generating cover image")
        pdfimage = outaudio.split(".")[0] + ".png"
        GenerateCoverImage(temp_pdf, pdfimage)

        if coverimage is None:
            coverimage = pdfimage        

    # print ("Text: ", text)
    # save the text to file
    with open("podcasttexx_pdf2text.txt", "w") as file:
        file.write(text)


    # create podcast ssml
    printwithtime("Creating podcast ssml")
    if callback is not None:
        callback("Creating podcast ssml")
    ssml = CreatePodcastSsml(text, callback)
    print(ssml)
    
    # generate podcast
    printwithtime("Generating podcast with Azure TTS")
    if callback is not None:
        callback("Generating podcast with Azure TTS")
    GenerateAudio(ssml, outaudio)
    if callback is not None:
        callback("Podcast audio generated.")

    # # generate video
    # printwithtime("Generating video")
    # GenerateVideo(outaudio, temp_pdf, outaudio.split(".")[0] + ".mp4")

def GenerateVideo(audiofile, pdffile, outvideo):
    from moviepy.editor import ImageClip, concatenate_videoclips, AudioClip, AudioFileClip




    # List to store individual image clips
    clips = []

    # get audio file duration
    from pydub import AudioSegment
    audio = AudioSegment.from_file(audiofile)
    duration = audio.duration_seconds

    import fitz
    if os.path.exists(pdffile):
        # open the pdf file
        pdf_document = fitz.open(pdffile)
        # number of pages
        num_pages = len(pdf_document) + 1

        if num_pages > 0:
            duration_per_page = duration / num_pages
    else:
        duration_per_page = duration

    # Create an ImageClip from each image
    # cover = "aiunboxed.png"
    cover = "GraphRAG-2404.png"
    if os.path.exists(cover):
        clip = ImageClip(cover, duration=duration_per_page)  # Duration of 3 seconds per image       
        clips.append(clip)

    # get cover image width and height
    cover_image = ImageClip(cover)
    cwidth, cheight = cover_image.size


    if os.path.exists(pdffile):
        for page in pdf_document:
            # get the first page
            first_page = page

            # get the image of the first page with high resolution
            image = first_page.get_pixmap(matrix=fitz.Matrix(2, 2))        

            img = "page.png"
            # save the image
            image.save(img)
            # Create an ImageClip from each image
            clip = ImageClip(img, duration=duration_per_page)  # Duration of 3 seconds per image       
            
            # resize the image to cover image size
            # resized_clip = clip.resize(height = cheight)
            # clips.append(resized_clip)
            
            clips.append(clip)

    # Concatenate the clips to form the final slideshow
    slideshow = concatenate_videoclips(clips, method="compose")

    # load audio file into audio clip
    audio_clip = AudioFileClip(audiofile)

    # Add the audio to the slideshow
    slideshow = slideshow.set_audio(audio_clip)
    
    # Export the video with animations with high compression    
    slideshow.write_videofile(outvideo, codec="libx264", fps = 4, threads=4)


# helper
def GeneratePodcastFromUrl(url, callback = None):
    _tmp_dir = "./tmp"
    if not os.path.exists(_tmp_dir):
        os.makedirs(_tmp_dir)
    os.chdir(_tmp_dir)
    # get the file name from url
    outaudio = None
    if outaudio is None:
        outaudio  = url.split("/")[-1].split(".")[0] + ".wav"
    GeneratePodcast(url, outaudio, callback=callback)
    return os.path.join(_tmp_dir, outaudio)
    # GenerateVideo(outaudio, "temp.pdf", outaudio.split(".")[0] + ".mp4")

# main func
if __name__ == "__main__":
    # only for debugging
    GeneratePodcastFromUrl("../data/test.pdf")
