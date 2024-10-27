import React, { useEffect, useRef } from 'react';

const SeaLevelMap = ({ latitude = 20, longitude = -80, zoom = 3 }) => {
  const mapDiv = useRef(null);
  const mapInstance = useRef(null);
  const viewInstance = useRef(null);

  useEffect(() => {
    // Load ArcGIS modules dynamically
    const loadMap = async () => {
      if (!mapInstance.current && !viewInstance.current) {
        try {
          const [ArcGISMap, MapView, FeatureLayer, Legend] = await Promise.all([
            import('https://js.arcgis.com/4.28/@arcgis/core/Map.js').then(m => m.default),
            import('https://js.arcgis.com/4.28/@arcgis/core/views/MapView.js').then(m => m.default),
            import('https://js.arcgis.com/4.28/@arcgis/core/layers/FeatureLayer.js').then(m => m.default),
            import('https://js.arcgis.com/4.28/@arcgis/core/widgets/Legend.js').then(m => m.default),
          ]);

          // Create the map
          mapInstance.current = new ArcGISMap({
            basemap: "streets-vector",
          });

          // Create the view
          viewInstance.current = new MapView({
            container: mapDiv.current,
            map: mapInstance.current,
            zoom: zoom,
            center: [longitude, latitude],
          });

          // Create the Feature Layer
          const featureLayer = new FeatureLayer({
            url: "https://www.coast.noaa.gov/arcgis/rest/services/dc_slr/slr_1ft/MapServer/0",
            opacity: 0.5,
          });

          // Add the Feature Layer to the map
          mapInstance.current.add(featureLayer);

          // Add a legend
          // const legend = new Legend({
          //   view: viewInstance.current,
          // });

          // viewInstance.current.ui.add(legend, "bottom-left");
        } catch (error) {
          console.error("Error loading map:", error);
        }
      } else if (viewInstance.current) {
        // Update the center and zoom if the map already exists
        // viewInstance.current.goTo({
        //   center: [longitude, latitude],
        //   zoom: zoom,
        // });
      }
    };

    loadMap();

    // Cleanup function
    // return () => {
    //   if (viewInstance.current && mapInstance.current) {
    //     viewInstance.current.destroy();
    //     viewInstance.current = null; // Clear the reference

    //     mapInstance.current.destroy();
    //     mapInstance.current = null; // Clear the reference
    //   }
    // };
  }); // Dependencies array includes coordinates and zoom

  return (
    <div 
      ref={mapDiv} 
      className=""
      style={{ padding: 0, margin: 0, maxHeight: "50vh" }}
    />
  );
};

export default SeaLevelMap;
