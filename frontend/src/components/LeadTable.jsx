import React from "react";

export default function LeadTable({ leads, loading, onRefresh }) {
    return (
        <div className="card">
            <div className="card-title" style={{ justifyContent: "space-between" }}>
                <span>📋 Captured Leads ({leads.length})</span>
                <button 
                    id="refresh-leads-button"
                    className="btn btn-ghost" 
                    onClick={onRefresh} 
                    style={{ padding: "6px 12px", fontSize: 12 }}
                >
                    ↻ Refresh
                </button>
            </div>

            {loading ? (
                <div className="empty-state">
                    <div className="spinner" style={{ margin: "0 auto" }} />
                </div>
            ) : leads.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon">📭</div>
                    <div className="empty-state-text">No leads captured yet. Send a message to start collecting!</div>
                </div>
            ) : (
                <div className="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Preferred Time</th>
                                <th>Website</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {leads.map(lead => (
                                <tr key={lead.id}>
                                    <td className="td-name">{lead.name}</td>
                                    <td className="td-email">{lead.email}</td>
                                    <td>{lead.phone}</td>
                                    <td>{lead.preferred_time}</td>
                                    <td className="text-sm" style={{ maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis" }}>
                                        {lead.website_url}
                                    </td>
                                    <td className="text-sm">{new Date(lead.created_at).toLocaleDateString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
