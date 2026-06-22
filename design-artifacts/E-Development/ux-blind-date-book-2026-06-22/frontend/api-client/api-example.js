// Example integration for the existing static prototype (plain JS)
const API_BASE = 'http://127.0.0.1:5000'

async function parseAgent(text){
  const res = await fetch(`${API_BASE}/api/parse`,{ method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ text }) })
  if(!res.ok) throw new Error('parse failed')
  return res.json()
}

async function aiDecide(preferences, recipient){
  const res = await fetch(`${API_BASE}/api/ai/decide`,{ method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ preferences, recipient_details: recipient }) })
  if(!res.ok) throw new Error('ai decide failed')
  return res.json()
}

async function doCheckout(cartItems, shipping, billing, payment){
  const payload = { cart: { items: cartItems }, shipping_address: shipping, billing_address: billing, payment_method: payment }
  const res = await fetch(`${API_BASE}/api/checkout`,{ method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) })
  if(!res.ok) throw new Error('checkout failed')
  return res.json()
}

// Example wiring for the prototype's agent submit (replace existing simulation):
async function submitAgentToApi(text){
  try{
    const parsed = await parseAgent(text)
    console.log('Parsed:', parsed)
    // show summary to user and call aiDecide if user confirms
    // const decision = await aiDecide(parsed.parsed, { name:'Recipient', age: 30 })
    // console.log('Decision', decision)
  }catch(e){
    console.error(e)
  }
}

// Export for console usage in the static prototype
window.BlindDateApi = { parseAgent, aiDecide, doCheckout, submitAgentToApi }
