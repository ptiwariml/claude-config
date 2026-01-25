---
name: nano-banana
description: >
  Generate images using Google Gemini's Nano Banana image generation APIs.
  Use this skill when building text-to-image generators, image editors, or any
  application that needs AI image generation. Supports gemini-2.5-flash-image
  (fast) and gemini-3-pro-image-preview (quality) models.
---

# Nano Banana Image Generation Skill

Generate production-ready images using Google Gemini's Nano Banana APIs. This skill covers everything from simple text-to-image generation to sophisticated iterative editing with multi-turn conversation.

---

## CRITICAL: Exact Model Names

**Use ONLY these exact model strings. Do not invent, guess, or add date suffixes.**

| Model String (use exactly) | Alias | Use Case |
|---------------------------|-------|----------|
| `gemini-2.5-flash-image` | Nano Banana | Fast iterations, drafts, high volume (~2-5s) |
| `gemini-3-pro-image-preview` | Nano Banana Pro | Quality output, text rendering, 2K/4K resolution |

**Common mistakes to avoid:**
- `gemini-2.5-flash-preview-05-20` — wrong, date suffixes are for text models
- `gemini-2.5-pro-image` — wrong, 2.5 Pro doesn't do image generation
- `gemini-3-flash-image` — wrong, doesn't exist
- `gemini-pro-vision` — wrong, that's for image *input*, not generation

---

## Quick Start: Standalone Node.js Script

This is the simplest way to generate an image and save it to disk:

```javascript
// generate-image.js
import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from "fs";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function generateImage(prompt, outputPath = "output.png") {
  const model = genAI.getGenerativeModel({
    model: "gemini-2.5-flash-image", // or "gemini-3-pro-image-preview" for quality
    generationConfig: {
      responseModalities: ["image", "text"],
    },
  });

  const response = await model.generateContent(prompt);
  const parts = response.response.candidates[0].content.parts;

  for (const part of parts) {
    if (part.inlineData) {
      const imageData = part.inlineData.data;
      const buffer = Buffer.from(imageData, "base64");
      fs.writeFileSync(outputPath, buffer);
      console.log(`Image saved to ${outputPath}`);
      return outputPath;
    }
  }

  throw new Error("No image generated");
}

// Usage
generateImage("A golden retriever playing in autumn leaves")
  .then(console.log)
  .catch(console.error);
```

**Run it:**
```bash
npm install @google/generative-ai
GEMINI_API_KEY=your_key_here node generate-image.js
```

---

## Quick Start: Next.js with AI SDK

### Server Action

```typescript
// app/actions/generate.ts
'use server'

import { google } from '@ai-sdk/google'
import { generateText } from 'ai'

export async function generateImage(prompt: string) {
  const result = await generateText({
    model: google('gemini-2.5-flash-image'),
    prompt,
    providerOptions: {
      google: {
        responseModalities: ['IMAGE'],
        imageConfig: { aspectRatio: '16:9' }
      }
    }
  })

  const imageFile = result.files[0]
  return {
    base64: imageFile.base64,
    dataUrl: `data:${imageFile.mediaType};base64,${imageFile.base64}`
  }
}
```

### Client Component

```typescript
// app/components/ImageGenerator.tsx
'use client'

import { useState } from 'react'
import { generateImage } from '../actions/generate'

export function ImageGenerator() {
  const [prompt, setPrompt] = useState('')
  const [imageUrl, setImageUrl] = useState('')
  const [loading, setLoading] = useState(false)

  const handleGenerate = async () => {
    if (!prompt.trim()) return
    setLoading(true)
    try {
      const result = await generateImage(prompt)
      setImageUrl(result.dataUrl)
    } catch (error) {
      console.error('Generation failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <input
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe your image..."
        disabled={loading}
      />
      <button onClick={handleGenerate} disabled={loading || !prompt.trim()}>
        {loading ? 'Generating...' : 'Generate'}
      </button>
      {imageUrl && <img src={imageUrl} alt="Generated" />}
    </div>
  )
}
```

---

## Model Selection Guide

| Use Case | Model | Why |
|----------|-------|-----|
| Rapid iterations, drafts | `gemini-2.5-flash-image` | Fast (2-5s), ~$0.039/image |
| Final output, quality | `gemini-3-pro-image-preview` | Superior quality, thinking |
| Text-heavy images | `gemini-3-pro-image-preview` | Best typography, 2K resolution |
| Multi-turn editing | Either | Both support conversational editing |
| High volume | `gemini-2.5-flash-image` | Lower cost, faster throughput |

---

## Image Configuration Options

### Aspect Ratios

```typescript
imageConfig: {
  aspectRatio: '1:1',   // 1024x1024 - icons, Instagram
  aspectRatio: '16:9',  // 1344x768 - YouTube, widescreen
  aspectRatio: '9:16',  // 768x1344 - TikTok, Stories
  aspectRatio: '4:3',   // 1184x864 - presentations
  aspectRatio: '21:9',  // 1536x672 - cinematic
}
```

### Resolution (Pro Only)

```typescript
imageConfig: {
  imageSize: '2K',  // Higher resolution output
}
```

### Response Modalities

```typescript
responseModalities: ['IMAGE'],           // Images only (saves tokens)
responseModalities: ['TEXT', 'IMAGE'],   // Both text and images
```

---

## Advanced: Image Editing (Multi-Turn)

Edit existing images conversationally:

```javascript
// edit-image.js
import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from "fs";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function editImage(imagePath, editPrompt, outputPath = "edited.png") {
  const model = genAI.getGenerativeModel({
    model: "gemini-2.5-flash-image",
    generationConfig: {
      responseModalities: ["image", "text"],
    },
  });

  // Read the input image
  const imageBuffer = fs.readFileSync(imagePath);
  const base64Image = imageBuffer.toString("base64");
  const mimeType = imagePath.endsWith(".png") ? "image/png" : "image/jpeg";

  const response = await model.generateContent([
    {
      inlineData: {
        mimeType: mimeType,
        data: base64Image,
      },
    },
    { text: editPrompt },
  ]);

  const parts = response.response.candidates[0].content.parts;

  for (const part of parts) {
    if (part.inlineData) {
      const buffer = Buffer.from(part.inlineData.data, "base64");
      fs.writeFileSync(outputPath, buffer);
      console.log(`Edited image saved to ${outputPath}`);
      return outputPath;
    }
  }

  throw new Error("No image generated");
}

// Usage
editImage("input.png", "Make the sky more dramatic with storm clouds")
  .then(console.log)
  .catch(console.error);
```

---

## Advanced: Next.js API Route with Streaming

```typescript
// app/api/generate/route.ts
import { google } from '@ai-sdk/google'
import { streamText } from 'ai'

export const maxDuration = 30

export async function POST(req: Request) {
  const { prompt, model = 'nano', aspectRatio = '1:1' } = await req.json()

  const modelName = model === 'pro'
    ? 'gemini-3-pro-image-preview'
    : 'gemini-2.5-flash-image'

  const result = streamText({
    model: google(modelName),
    prompt,
    providerOptions: {
      google: {
        responseModalities: ['IMAGE', 'TEXT'],
        imageConfig: { aspectRatio }
      }
    }
  })

  return result.toDataStreamResponse()
}
```

---

## Advanced: Batch Generation

```typescript
async function generateBatch(prompts: string[]) {
  const results = []

  for (const prompt of prompts) {
    try {
      const result = await generateImage(prompt)
      results.push({ prompt, success: true, ...result })
    } catch (error) {
      results.push({ prompt, success: false, error: error.message })
    }
    // Rate limit: wait between requests
    await new Promise(r => setTimeout(r, 1000))
  }

  return results
}
```

---

## Environment Setup

```bash
# .env or .env.local
GEMINI_API_KEY=your_api_key_here

# For Vercel Blob storage (optional)
BLOB_READ_WRITE_TOKEN=your_vercel_token

# For rate limiting with Upstash (optional)
UPSTASH_REDIS_REST_URL=your_url
UPSTASH_REDIS_REST_TOKEN=your_token
```

### Install Dependencies

**For standalone Node.js:**
```bash
npm install @google/generative-ai
```

**For Next.js with AI SDK:**
```bash
npm install @ai-sdk/google ai @ai-sdk/react
```

---

## Rate Limits & Costs

### Free Tier
- Nano Banana: ~100 requests/day, 15 requests/minute
- Nano Banana Pro: ~10 requests/day, 5-10 requests/minute

### Cost Estimates
- ~1,290 tokens per image
- Nano Banana: ~$0.039 per image
- Nano Banana Pro: Higher cost for 2K/4K output

### Rate Limit Handling

```typescript
async function generateWithRetry(prompt: string, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await generateImage(prompt)
    } catch (error) {
      if (error.message?.includes('429') && i < maxRetries - 1) {
        // Rate limited - wait and retry
        await new Promise(r => setTimeout(r, 2000 * (i + 1)))
        continue
      }
      throw error
    }
  }
}
```

---

## Error Handling

```typescript
function handleGenerationError(error: any) {
  if (error.message?.includes('429')) {
    return { error: 'Rate limited. Please wait a moment and try again.' }
  }
  if (error.message?.includes('401')) {
    return { error: 'Invalid API key. Check your GEMINI_API_KEY.' }
  }
  if (error.message?.includes('400')) {
    return { error: 'Content policy violation. Please modify your prompt.' }
  }
  return { error: 'Generation failed. Please try again.' }
}
```

---

## Anti-Patterns to Avoid

| Don't | Do Instead |
|-------|-----------|
| Invent model names or add date suffixes | Use exactly `gemini-2.5-flash-image` or `gemini-3-pro-image-preview` |
| Store base64 in database | Store in object storage (Vercel Blob/S3), save URL only |
| Skip rate limit handling | Implement retry logic with backoff |
| Hardcode API keys client-side | Use server actions/API routes with env variables |
| Generate on every keystroke | Debounce, require explicit action |
| No loading states | Show progress (generation takes 5-30s) |

---

## Complete Working Example

Save this as `nano-banana-demo.js`:

```javascript
import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from "fs";
import path from "path";

// Initialize the API
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// Configuration
const CONFIG = {
  model: "gemini-2.5-flash-image", // "gemini-3-pro-image-preview" for quality
  outputDir: "./generated-images",
};

// Ensure output directory exists
if (!fs.existsSync(CONFIG.outputDir)) {
  fs.mkdirSync(CONFIG.outputDir, { recursive: true });
}

async function generate(prompt, filename) {
  console.log(`Generating: "${prompt}"`);

  const model = genAI.getGenerativeModel({
    model: CONFIG.model,
    generationConfig: {
      responseModalities: ["image", "text"],
    },
  });

  const response = await model.generateContent(prompt);
  const parts = response.response.candidates[0].content.parts;

  for (const part of parts) {
    if (part.inlineData) {
      const outputPath = path.join(CONFIG.outputDir, filename);
      const buffer = Buffer.from(part.inlineData.data, "base64");
      fs.writeFileSync(outputPath, buffer);
      console.log(`Saved: ${outputPath}`);
      return outputPath;
    }
    if (part.text) {
      console.log(`Model response: ${part.text}`);
    }
  }

  throw new Error("No image in response");
}

// Demo: Generate multiple images
async function demo() {
  const prompts = [
    { prompt: "A serene mountain lake at sunrise with mist", file: "lake.png" },
    { prompt: "A cozy coffee shop interior, warm lighting", file: "cafe.png" },
    { prompt: "A futuristic cityscape with flying vehicles", file: "city.png" },
  ];

  for (const { prompt, file } of prompts) {
    try {
      await generate(prompt, file);
      // Rate limit pause
      await new Promise((r) => setTimeout(r, 2000));
    } catch (error) {
      console.error(`Failed: ${prompt}`, error.message);
    }
  }

  console.log("Done!");
}

demo();
```

**Run:**
```bash
npm install @google/generative-ai
GEMINI_API_KEY=your_key node nano-banana-demo.js
```

---

## Key Principles

1. **Use exact model names** - `gemini-2.5-flash-image` or `gemini-3-pro-image-preview`
2. **Handle rate limits** - Implement retry with exponential backoff
3. **Choose model wisely** - Nano Banana for speed, Pro for quality
4. **Server-side only** - Never expose API keys to the client
5. **Store images externally** - Use blob storage, not base64 in databases
6. **Show loading states** - Generation takes 5-30 seconds
7. **Leverage conversation** - Use multi-turn for iterative editing

---

## References

- [Gemini API Models](https://ai.google.dev/gemini-api/docs/models)
- [Nano Banana Documentation](https://ai.google.dev/gemini-api/docs/nanobanana)
- [AI SDK Google Provider](https://sdk.vercel.ai/providers/ai-sdk-providers/google-generative-ai)
