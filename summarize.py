import google.generativeai as genai
import asyncio
from pyppeteer import launch
import config


async def scrape_reviews(url):
    reviews = []
    browser = None

    try:
        browser = await launch({"headless": True, "args": ["--window-size=800,3200"]})
        page = await browser.newPage()
        await page.setViewport({"width": 800, "height": 3200})
        await page.goto(url)
        await page.waitForSelector('.jftiEf', timeout=5000)
        elements = await page.querySelectorAll('.jftiEf ')

        if not elements:
            print("No reviews found for this place.")
            await browser.close()
            return reviews

        for element in elements:
            try:
                await page.waitForSelector('.w8nwRe', timeout=3000)
                more_btn = await element.querySelector('.w8nwRe')
                if more_btn is not None:
                    await page.evaluate('button => button.click()', more_btn)
                    await page.waitFor(5000)
            except:
                pass

            try:
                await page.waitForSelector('.MyEned', timeout = 3000)
                snippet = await element.querySelector('.MyEned')
                text = await page.evaluate('selected => selected.textContent', snippet)

                reviews.append(text)
            except:
                print("error in extracting reviews")
            
    except:
        print("No reviews found")
    
    finally:
        if browser:
            await browser.close()

    return reviews


def summarize(reviews, model):
    prompt = "I collected some reviews of a place I was considering visiting. Can you summarize \
              the reviews for me? Don't write the summary in bullet points. write as a paragraph. \
              below are the reviews:\n"
    for review in reviews:
        prompt += "\n" + review
    response = model.generate_content(
    prompt,
    generation_config=genai.types.GenerationConfig(
        max_output_tokens=300,
        temperature=0,
    ),
)

    return response.text
    
genai.configure(api_key=config.API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


url = input("Enter the url: ")
reviews = asyncio.run(scrape_reviews(url))

if reviews:
    result = summarize(reviews, model)
    print(result)
