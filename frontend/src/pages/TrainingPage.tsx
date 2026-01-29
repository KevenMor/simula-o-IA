import { useState, useEffect } from 'react'
import { Plus, Trash2, Edit2 } from 'lucide-react'
import { getDocuments, saveDocument, deleteDocument } from '../services/api'

export default function TrainingPage() {
  const [tenantId, setTenantId] = useState('autoescola_ideal')
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [editingDoc, setEditingDoc] = useState<any>(null)
  const [formData, setFormData] = useState({
    title: '',
    category: 'geral',
    content: '',
  })

  useEffect(() => {
    loadDocuments()
  }, [tenantId])

  const loadDocuments = async () => {
    setLoading(true)
    try {
      const data = await getDocuments(tenantId)
      setDocuments(data)
    } catch (error) {
      console.error('Error loading documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      await saveDocument({
        tenant_id: tenantId,
        ...formData,
        id: editingDoc?.id,
      })
      setShowForm(false)
      setEditingDoc(null)
      setFormData({ title: '', category: 'geral', content: '' })
      loadDocuments()
    } catch (error) {
      console.error('Error saving document:', error)
    }
  }

  const handleDelete = async (docId: string) => {
    if (!confirm('Tem certeza que deseja excluir este documento?')) return
    try {
      await deleteDocument(tenantId, docId)
      loadDocuments()
    } catch (error) {
      console.error('Error deleting document:', error)
    }
  }

  const handleEdit = (doc: any) => {
    setEditingDoc(doc)
    setFormData({
      title: doc.title,
      category: doc.category,
      content: doc.content,
    })
    setShowForm(true)
  }

  return (
    <div className="max-w-6xl">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Treinamento IA</h1>
          <p className="text-gray-600">Gerencie a base de conhecimento do agente</p>
        </div>
        <div className="flex items-center gap-4">
          <input
            type="text"
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg"
            placeholder="ID do cliente"
          />
          <button
            onClick={() => {
              setShowForm(true)
              setEditingDoc(null)
              setFormData({ title: '', category: 'geral', content: '' })
            }}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            <Plus size={20} />
            Novo Documento
          </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">
            {editingDoc ? 'Editar' : 'Novo'} Documento
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Título</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Categoria</label>
              <input
                type="text"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Conteúdo</label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                rows={10}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg font-mono text-sm"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Salvar
              </button>
              <button
                onClick={() => {
                  setShowForm(false)
                  setEditingDoc(null)
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">Carregando...</div>
      ) : (
        <div className="space-y-4">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{doc.title}</h3>
                  <p className="text-sm text-gray-500">Categoria: {doc.category}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(doc)}
                    className="p-2 text-primary-600 hover:bg-primary-50 rounded"
                  >
                    <Edit2 size={18} />
                  </button>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
              <div className="mt-4 p-4 bg-gray-50 rounded border border-gray-200">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                  {doc.content.substring(0, 500)}
                  {doc.content.length > 500 && '...'}
                </pre>
              </div>
            </div>
          ))}
          {documents.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              Nenhum documento cadastrado ainda
            </div>
          )}
        </div>
      )}
    </div>
  )
}
