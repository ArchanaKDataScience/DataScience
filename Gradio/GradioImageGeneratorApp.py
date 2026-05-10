from Model import generate_image
import gradio as gr

with gr.Blocks() as demo:
    gr.Markdown("## Image Generator using Gradio")
    with gr.Row():
        prompt = gr.Textbox(label="Enter a prompt to generate an image")
        generate_button = gr.Button("Generate Image")
 
    output_image = gr.Image(label="Generated Image")

    generate_button.click(generate_image, inputs=prompt, outputs=output_image)
   
demo.launch(share=True)