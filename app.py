from fastapi import FastAPI, Request, HTTPException
import os
import logging
import requests
import aiohttp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/analyze")
async def analyze_sentiment(request: Request):
    try:
        data = await request.json()
        symbol = data.get('symbol')
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol is required")
            
        # Format symbol to handle both formats (EUR/USD and EURUSD)
        formatted_symbol = symbol.replace("/", "")
        logger.info(f"Received request to analyze sentiment for {symbol} (formatted: {formatted_symbol})")
        
        sentiment = await analyze_market_sentiment(formatted_symbol)
        logger.info(f"Sentiment analysis completed for {symbol}")
        
        return {"symbol": symbol, "sentiment": sentiment}
    except Exception as e:
        logger.error(f"Error in analyze_sentiment: {str(e)}")
        return {"error": str(e), "symbol": data.get('symbol'), "sentiment": "Market sentiment analysis temporarily unavailable"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

async def analyze_market_sentiment(symbol):
    """Analyze market sentiment using OpenAI API"""
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Analyze the current market sentiment for {symbol} based on recent news and market data.
        
        Provide your analysis in exactly this format:

        📈 Market Sentiment:
        • Direction: [Bullish/Bearish/Neutral]  # MUST start with exactly "Direction: "
        • Strength: [Strong/Moderate/Weak]
        • Key drivers: [Brief explanation]

        💡 Trading Implications:
        • Short-term outlook
        • Risk assessment
        • Key levels to watch

        ⚠️ Risk Factors:
        • List 2-3 key risks that could affect the price
        • Focus on immediate threats

        🎯 Conclusion:
        A brief 2-3 line summary of the overall sentiment and key action points.

        Keep the response concise and focused. Do not use markdown formatting (no ### or **).
        Do not add any additional sections or conclusions.
        """
        
        data = {
            "model": "gpt-4-0125-preview",
            "messages": [
                {"role": "system", "content": "You are a professional market analyst providing concise, actionable market analysis."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        logger.info(f"Sending request to OpenAI API for {symbol}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                response_text = await response.text()
                logger.info(f"OpenAI API response status: {response.status}")
                logger.info(f"OpenAI API response: {response_text}")
                
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    logger.error(f"OpenAI API error: {response.status} - {response_text}")
                    return f"Market sentiment analysis temporarily unavailable (Error: {response.status})"
                    
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return f"Market sentiment analysis temporarily unavailable (Error: {str(e)})"

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting news service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 