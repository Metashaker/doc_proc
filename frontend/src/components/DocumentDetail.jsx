import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { addTag, deleteDocument, getDocument, getTags, removeTag } from '../api'

function DocumentDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [document, setDocument] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [tagName, setTagName] = useState('')
  const [tagError, setTagError] = useState(null)
  const [availableTags, setAvailableTags] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)

  useEffect(() => {
    loadDocument()
  }, [id])

  useEffect(() => {
    loadAvailableTags()
  }, [id])

  async function loadDocument() {
    try {
      setLoading(true)
      const data = await getDocument(id)
      setDocument(data)
    } catch (err) {
      setError(err.message || 'Failed to load document')
    } finally {
      setLoading(false)
    }
  }

  async function loadAvailableTags() {
    try {
      const data = await getTags()
      setAvailableTags(data)
    } catch (err) {
      setAvailableTags([])
    }
  }

  async function handleDelete() {
    if (!confirm('Are you sure you want to delete this document?')) {
      return
    }
    try {
      await deleteDocument(id)
      navigate('/')
    } catch (err) {
      setError(err.message || 'Failed to delete document')
    }
  }

  async function handleAddTag(e) {
    e.preventDefault()
    if (!tagName.trim()) return
    try {
      setTagError(null)
      const created = await addTag(id, tagName)
      setDocument((prev) => ({
        ...prev,
        tags: [...(prev?.tags || []), created],
      }))
      setAvailableTags((prev) => {
        if (prev.some((tag) => tag.id === created.id)) {
          return prev
        }
        return [...prev, created]
      })
      setTagName('')
      setShowSuggestions(false)
    } catch (err) {
      setTagError(err.message || 'Failed to add tag')
    }
  }

  async function handleRemoveTag(tagId) {
    try {
      await removeTag(id, tagId)
      setDocument((prev) => ({
        ...prev,
        tags: prev.tags.filter(tag => tag.id !== tagId),
      }))
    } catch (err) {
      setTagError(err.message || 'Failed to remove tag')
    }
  }

  if (loading) {
    return <div className="loading">Loading document...</div>
  }

  if (error) {
    return <div className="error">{error}</div>
  }

  if (!document) {
    return <div className="error">Document not found</div>
  }

  const suggestions = filteredTags(availableTags, tagName, document.tags || [])

  return (
    <div className="document-detail">
      <h2>{document.filename}</h2>
      <div className="meta">
        <p>Status: {document.status}</p>
        <p>Pages: {document.page_count || 'Unknown'}</p>
        <p>Size: {formatFileSize(document.file_size)}</p>
        <p>Uploaded: {new Date(document.created_at).toLocaleString()}</p>
      </div>
      <h3>Extracted Content</h3>
      <div className="content">
        {document.content || 'No content extracted'}
      </div>
      <div className="tag-section">
        <h3>Tags</h3>
        {tagError && <div className="error">{tagError}</div>}
        {document.tags?.length > 0 ? (
          <div className="tag-list">
            {document.tags.map(tag => (
              <span key={tag.id} className="tag-pill">
                {tag.name}
                <button
                  type="button"
                  className="tag-remove"
                  onClick={() => handleRemoveTag(tag.id)}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        ) : (
          <div className="tag-empty">No tags yet.</div>
        )}
        <form className="tag-form" onSubmit={handleAddTag}>
          <div className="tag-input-wrapper">
            <input
              type="text"
              placeholder="Add a tag"
              value={tagName}
              onChange={(e) => {
                setTagName(e.target.value)
                setShowSuggestions(true)
              }}
              onFocus={() => setShowSuggestions(true)}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
            />
            {showSuggestions && tagName.trim() && (
              <div className="tag-suggestions">
                {suggestions.map(tag => (
                  <button
                    key={tag.id}
                    type="button"
                    className="tag-suggestion"
                    onMouseDown={() => setTagName(tag.name)}
                  >
                    {tag.name}
                  </button>
                ))}
                {suggestions.length === 0 && (
                  <div className="tag-suggestion empty">No matching tags</div>
                )}
              </div>
            )}
          </div>
          <button type="submit" className="tag-submit">Add</button>
        </form>
      </div>
      <div className="actions">
        <button className="back-btn" onClick={() => navigate('/')}>
          Back to List
        </button>
        <button className="delete-btn" onClick={handleDelete}>
          Delete Document
        </button>
      </div>
    </div>
  )
}

function formatFileSize(bytes) {
  if (!bytes) return 'Unknown size'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function filteredTags(availableTags, query, currentTags) {
  const normalized = query.trim().toLowerCase()
  const currentIds = new Set(currentTags.map(tag => tag.id))
  return availableTags.filter(tag => {
    if (currentIds.has(tag.id)) return false
    if (!normalized) return true
    return tag.name.toLowerCase().includes(normalized)
  })
}

export default DocumentDetail
