import { Application, Router } from "https://deno.land/x/oak@v16.1.0/mod.ts"
import "https://deno.land/std@0.224.0/dotenv/load.ts"
import { OpenAI } from "https://deno.land/x/openai@v4.52.3/mod.ts"


const app = new Application()
const router = new Router()

router.get("/", (context) => {
    context.response.body = "Hello, world!"
})

router.post("/chat", async (context) => {
    const { request, response } = context
    if (!request.hasBody) {
        response.status = 400
        response.body = { message: "Invalid request" }
        return
    }
    
    const { prompt } = await request.body.json()
    const chatResponse = await getChatResponse(prompt)
    response.body = { response: chatResponse }
})

app.use(router.routes())
app.use(router.allowedMethods())

const PORT = 8000
console.log(`Server running on port ${PORT}`)
await app.listen({ port: PORT })


async function getChatResponse(prompt: string): Promise<string> {
    const OPENAI_API_KEY = Deno.env.get("OPENAI_API_KEY")
    const openai = new OpenAI({
        apiKey: OPENAI_API_KEY
    })
    
    const response = await openai.chat.completions.create({
        messages: [{ role: "user", content: prompt }],
        model: "gpt-4o"
    })

    if (!response.choices[0].message.content) {
        throw new Error("Error fetching response from OpenAI")
    }

    return response.choices[0].message.content
}
