import { useState, useEffect } from "react";
import { getLeads } from "../api/client";

export function useLeads() {
    const [leads, setLeads] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const refresh = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getLeads();
            setLeads(data);
        } catch (err) {
            setError(err.message || "Failed to fetch leads");
            setLeads([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        refresh();
    }, []);

    return { leads, loading, error, refresh };
}
