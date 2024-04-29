# Video Marketing Solution

## Introduction 
While advancements in AI have made video generation incredibly accessible to the public, yet the creation of a compelling marketing video still hinges on a well-crafted storyline and a deep understanding of the target audience. AIs are a powerful tool in helping artists reach their full creativity and expressibility by allowing them to experiment with different scenarios or backgrounds that may not be possible with traditional methods. Thus, this proposal can be seen as an iterative collaboration between humans and AI.  

## Technical Approach
###	Getting to know the product 
From an ad agency standpoint, it is of utmost importance to get to know the product and the message we hope to convey in promoting this product. Questions that need to be answered include how it betters one’s life or how it increases one life’s value. Along with its key features and Unique Selling Points (USPs), with the help of Large Language Models (LLMs), we can extract/generate keyphrases that will become the theme of the video. 

### Getting to know the product's audience 
By learning about user data, preferences, and the latest trends, we can incorporate this knowledge into the video-generating process to increase effectiveness. For example, incorporating recent trending aesthetics can help increase its explorability. 

###	Style Guide 
This is where the colour palette, typography, and imagery are developed as a style guide. Note that it requires consistency with brand identity and aesthetics to reinforce brand recognition and recall. The output can be a style preset that will become a reference image for storyboard generation.  

###	Storyboard and Text Prompt Integration
With the extracted theme and style guide, the initial scripts can be generated using LLMs. This includes key story elements, dialogue, and action sequences. This is where LLMs can be the most helpful given its speed in generating different ideas. A continuous refinement between humans and AI here is supposedly the most important part of this process. 

The script will then be turned into storyboards using Diffusion models such as Midjourney or Dall-E 2. It is incredibly important to be exhaustively detailed with prompting to achieve the desired results. Usage such as powerful words, negative words, as well as descriptions of lightning and angles will further narrow the creation to the specific concepts that we’re trying to achieve. The images generated will become the first frame in each scene.


### Video Generation 
At this point, we should have a visual representation of what we’re trying to achieve. Using RunwayML, Pika Labs, or AnimateDiff, each storyboard image can then be turned into moving videos. 


### Video Editing 
With the produced video segments, we can further leverage AI technologies in editing each video which can be difficult in traditional video editing methods such as frame interpolation to increase the length of the video.    

### Background Music 
Using Suno AI to create music that is fitting to the movements of the video that can incorporate sensory stimuli and further evoke emotions. 

## Potential Challenges
- Length of each scene: With RunwayML, each video generation can be a maximum of 4 seconds long. With further frame interpolation, we can increase the video length to a maximum of 16 seconds. However, as users, we cannot control the movements added in this lengthening process. Thus, a longer scene with particular movements can be difficult to achieve with existing services.  
- Consistency between each scene and Cohesiveness: Colours and lighting changes between scenes are also an apparent problem with current services. 

## Marketing Effectiveness 
The ability to convey storylines and overall cohesiveness is still the most important part in determining market effectiveness and this lays largely on the person putting everything together. However, with the above proposal, the continuous refinement of prompts and the abundance of ideas, as well as the shortened latency from ideas to videos will allow experiments of ideas more than before. 