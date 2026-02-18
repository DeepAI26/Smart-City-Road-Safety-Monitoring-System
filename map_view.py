import folium 
from folium import Element

def create_map(G, route_path=None, mode="select"):
    """
    mode = "select"  -> user clicks to choose start & end points
    mode = "route"   -> display computed route
    """

    # Center map
    lats = [G.nodes[n].get("latitude", G.nodes[n].get("lat", 0)) for n in G.nodes]
    lons = [G.nodes[n].get("longitude", G.nodes[n].get("lon", 0)) for n in G.nodes]

    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # ---- Draw road nodes ----
    for node, data in G.nodes(data=True):
        safety = float(data.get("safety", 1.0))

        if safety >= 0.7:
            color = "green"
        elif safety >= 0.4:
            color = "orange"
        else:
            color = "red"

        lat = data.get("latitude", data.get("lat", 0))
        lon = data.get("longitude", data.get("lon", 0))
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color=color,
            fill=True,
            fill_opacity=0.8,
            popup=f"Safety: {safety:.2f}"
        ).add_to(m)

    # ---- Draw route if provided ----
    if route_path:
        route_coords = [
            (G.nodes[n].get("latitude", G.nodes[n].get("lat", 0)),
             G.nodes[n].get("longitude", G.nodes[n].get("lon", 0)))
            for n in route_path
        ]

        folium.PolyLine(
            route_coords,
            color="blue",
            weight=5,
            opacity=0.9
        ).add_to(m)

    # ---- Enable pin dropping (for selection mode) ----
    if mode == "select":
        click_js = """
        <script>
        (function() {
            let clickCount = 0;
            let markers = [];
            let mapReady = false;

            // Function to attach click handler
            function attachClickHandler() {
                if (typeof map !== 'undefined' && map) {
                    map.on('click', function(e) {
                        const lat = parseFloat(e.latlng.lat.toFixed(6));
                        const lng = parseFloat(e.latlng.lng.toFixed(6));

                        console.log('Map clicked:', lat, lng);

                        // Send message to parent window
                        if (window.parent && window.parent !== window) {
                            window.parent.postMessage(
                                {lat: lat, lng: lng},
                                "*"
                            );
                            console.log('Message sent to parent');
                        }

                        // Add marker
                        if (clickCount === 0) {
                            // Clear previous markers
                            markers.forEach(function(m) { map.removeLayer(m); });
                            markers = [];
                            
                            const marker = L.marker([lat, lng]).addTo(map);
                            marker.bindPopup("Start Point").openPopup();
                            markers.push(marker);
                            clickCount++;
                        } else if (clickCount === 1) {
                            const marker = L.marker([lat, lng]).addTo(map);
                            marker.bindPopup("End Point").openPopup();
                            markers.push(marker);
                            clickCount = 0; // Reset for next route
                        }
                    });
                    mapReady = true;
                    console.log('Click handler attached');
                }
            }

            // Try multiple times to attach handler
            function tryAttach() {
                if (!mapReady) {
                    attachClickHandler();
                    if (!mapReady) {
                        setTimeout(tryAttach, 200);
                    }
                }
            }

            // Start trying after a short delay
            setTimeout(tryAttach, 1000);
        })();
        </script>
        """

        m.get_root().html.add_child(Element(click_js))

    return m
