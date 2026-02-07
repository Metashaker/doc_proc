import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getDocuments, getDocumentsByTag } from '../api'

function DocumentList({ refreshKey }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [tags, setTags] = useState([])
  const [selectedTag, setSelectedTag] = useState('')

  useEffect(() => {
    loadDocuments()
  }, [refreshKey, selectedTag])


  async function loadDocuments() {
    try {
      setLoading(true)
      const data = selectedTag
        ? await getDocumentsByTag(selectedTag)
        : await getDocuments()
      setDocuments(data)
      if (!selectedTag) {
        const tagMap = new Map()
        data.forEach((doc) => {
          (doc.tags || []).forEach((tag) => {
            if (!tagMap.has(tag.id)) {
              tagMap.set(tag.id, tag)
            }
          })
        })
        setTags(Array.from(tagMap.values()))
      }
    } catch (err) {
      setError(err.message || 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }


  if (loading) {
    return <div className="loading">Loading documents...</div>
  }

  if (error) {
    return <div className="error">{error}</div>
  }

  return (
    <div className="document-list">
      <div className="document-list-header">
        <h2>Documents</h2>
        <label className="tag-filter">
          <span>Filter by tag</span>
          <select
            value={selectedTag}
            onChange={(e) => setSelectedTag(e.target.value)}
          >
            <option value="">All</option>
            {tags.map(tag => (
              <option key={tag.id} value={tag.name}>{tag.name}</option>
            ))}
          </select>
        </label>
      </div>
      {documents.length === 0 ? (
        <div className="empty-state">
          No documents uploaded yet. Upload a PDF to get started.
        </div>
      ) : (
        documents.map(doc => (
          <div key={doc.id} className="document-item">
            <div>
              <Link to={`/documents/${doc.id}`}>{doc.filename}</Link>
              <div className="document-meta">
                {doc.page_count} pages | {formatFileSize(doc.file_size)} | {doc.status}
              </div>
              {doc.tags?.length > 0 && (
                <div className="tag-list">
                  {doc.tags.map(tag => (
                    <span key={tag.id} className="tag-pill">{tag.name}</span>
                  ))}
                </div>
              )}
            </div>
            <div className="document-meta">
              {new Date(doc.created_at).toLocaleDateString()}
            </div>
          </div>
        ))
      )}
    </div>
  )
}

function formatFileSize(bytes) {
  if (!bytes) return 'Unknown size'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

export default DocumentList
