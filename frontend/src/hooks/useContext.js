import { useRef, useState } from "react";
import {
  retrieveContext as fetchContext,
} from "../api/client";



function useContext() {
    const [state, setState] = useState("sources");
    const [sources, setSources] = useState([]);
    const [query, setQuery] = useState("");

    const requestIdRef = useRef(0);

    const updateContext = (
        newSources,
        newQuery = ""
    ) => {
        setSources(newSources);
        setQuery(newQuery);

        setState(
        newSources.length > 0
            ? "sources"
            : "empty"
        );
    };

    const clearContext = () => {
        // Invalidate any retrieval that is currently running.
        requestIdRef.current += 1;

        setSources([]);
        setQuery("");
        setState("empty");
    };

    const retrieveContext = async (
        newQuery,
        projectId
    ) => {
        if (!newQuery?.trim()) {
            return;
        }

        const requestId =
            ++requestIdRef.current;

        setState("loading");
        setQuery(newQuery);

        try {
            const result =
                await fetchContext(newQuery, projectId);

            // Ignore stale retrieval results.
            if (
                requestId !== requestIdRef.current  
            ) {
                return;
            }

            const newSources =
                (result.sources || []).map((source) => ({
                    id: source.id,
                    fileName: source.file_name,
                    filePath: source.file_path,
                    relevance: source.relevance,
                    content: source.content,
                }));

            updateContext(
                newSources,
                result.query || newQuery
            );
        } catch (error) {
            console.error(
                    "Failed to retrieve context:",
                error
            );

            // Only update the UI if this is
            // still the latest request.
            if (
                requestId !== requestIdRef.current
            ) {
                return;
            }

            setSources([]);
            setState("empty");
        }
    };

    return {
        state,
        sources,
        query,
        retrieveContext,
        updateContext,
        clearContext,
    };
    }

export default useContext;