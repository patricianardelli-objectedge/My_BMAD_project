// Lightweight TypeScript HTTP client for key Blind Date Book endpoints
// Usage: compile with tsc and import into your frontend build.

export type PreferenceObject = {
  recipient_type?: 'self'|'gift'
  recipient_age_range?: string
  genres?: string[]
  avoid?: string[]
  surprise_level?: 'light_hint'|'moderate'|'full'
  raw_input: string
}

export type RecipientDetails = {
  name?: string
  age?: number
  relationship?: string
}

export type BookCandidate = {
  book_id: string
  title: string
  score?: number
  reason?: Record<string, any>
}

export type Address = {
  line1?: string
  line2?: string
  city?: string
  region?: string
  postal_code?: string
  country?: string
}

export type CartItem = { book_id: string, qty: number, price_cents: number }

export type PaymentCreditCard = { type: 'credit_card', token: string, cardholder_name?: string }
export type PaymentPIX = { type: 'pix', pix_key?: string }
export type PaymentMethod = PaymentCreditCard | PaymentPIX

export class ApiClient {
  baseUrl: string
  token?: string
  constructor(baseUrl = ''){ this.baseUrl = baseUrl }
  setToken(t: string){ this.token = t }

  private headers(){
    const h: Record<string,string> = { 'Content-Type':'application/json' }
    if(this.token) h['Authorization'] = `Bearer ${this.token}`
    return h
  }

  async parseAgent(text: string, session_id?: string){
    const res = await fetch(`${this.baseUrl}/api/agent/parse`,{
      method: 'POST', headers:this.headers(), body: JSON.stringify({ text, session_id })
    })
    if(!res.ok) throw new Error(`parseAgent failed: ${res.status}`)
    return res.json() as Promise<{ parsed: PreferenceObject, follow_up_question?: string, suggestions?: string[] }>
  }

  async aiDecide(payload: { preferences: PreferenceObject, recipient_details?: RecipientDetails, exclude_books?: string[], allow_explicit?: boolean, max_candidates?: number }){
    const res = await fetch(`${this.baseUrl}/api/ai/decide`,{ method:'POST', headers:this.headers(), body: JSON.stringify(payload) })
    if(!res.ok) throw new Error(`aiDecide failed: ${res.status}`)
    return res.json() as Promise<{ book_id: string, title: string, score: number, reason: any, candidates: BookCandidate[] }>
  }

  async checkout(payload: { cart: { items: CartItem[] }, shipping_address: Address, billing_address?: Address, recipient_details?: RecipientDetails, payment_method: PaymentMethod, metadata?: any }){
    const res = await fetch(`${this.baseUrl}/api/checkout`,{ method:'POST', headers:this.headers(), body: JSON.stringify(payload) })
    if(!res.ok){
      const text = await res.text()
      throw new Error(`checkout failed: ${res.status} ${text}`)
    }
    return res.json() as Promise<{ order_id: string, payment_status: string, tracking?: any }>
  }
}

// Example: const client = new ApiClient('http://localhost:8000'); client.parseAgent('...')
