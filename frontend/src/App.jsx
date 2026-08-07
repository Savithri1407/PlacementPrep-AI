import React, {useState, useEffect} from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App(){
  const [files, setFiles] = useState([])
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(()=>{
    fetch(`${API_BASE}/history`).then(r=>r.json()).then(data=>{
      if(data.history) setMessages(data.history)
    }).catch(()=>{})
  },[])

  const handleFileChange = (e)=>{
    setFiles(e.target.files)
  }

  const handleUpload = async ()=>{
    if(!files || files.length===0) return
    const fd = new FormData()
    for(const f of files) fd.append('files', f)
    setLoading(true)
    const res = await fetch(`${API_BASE}/upload`, {method:'POST', body: fd})
    const data = await res.json()
    setLoading(false)
    alert('Uploaded: '+ (data.uploaded||[]).join(', '))
  }

  const handleAsk = async ()=>{
    if(!question) return
    setLoading(true)
    const res = await fetch(`${API_BASE}/ask`, {
      method:'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({question}),
    })
    const data = await res.json()
    setLoading(false)
    const userMsg = {role:'user', content: question}
    const assistantMsg = {role:'assistant', content: data.answer}
    setMessages(prev => [...prev, userMsg, assistantMsg])
    setQuestion('')
  }

  const handleClear = async ()=>{
    await fetch(`${API_BASE}/clear`, {method:'POST'})
    setMessages([])
  }

  return (
    <div className="container">
      <h1>PlacementPrep AI</h1>

      <section className="upload">
        <h2>Upload PDFs</h2>
        <input type="file" multiple accept="application/pdf" onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={loading}>Upload & Index</button>
      </section>

      <section className="chat">
        <h2>Chat</h2>
        <div className="messages">
          {messages.map((m, i)=>(
            <div key={i} className={`message ${m.role}`}>
              <strong>{m.role}:</strong>
              <div>{m.content}</div>
            </div>
          ))}
        </div>

        <textarea value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Ask about DSA, DBMS, OS, CN, Java..." />
        <div className="controls">
          <button onClick={handleAsk} disabled={loading}>Ask</button>
          <button onClick={handleClear}>Clear</button>
        </div>
      </section>
    </div>
  )
}
