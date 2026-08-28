import { useEffect } from "react";

import {
  MapContainer,
  TileLayer,
  FeatureGroup,
  useMap,
} from "react-leaflet";

import { EditControl } from "react-leaflet-draw";

import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";


function MapResizeHandler() {
  const map = useMap();

  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 100);

    return () => clearTimeout(timer);
  }, [map]);

  return null;
}


function AreaSelector({
  value,
  onChange,
  disabled,
}) {
  const defaultCenter = [32.225, -110.9725];


  function handleCreated(event) {
    const layer = event.layer;

    if (!layer.toGeoJSON) {
      return;
    }

    const geojson = layer.toGeoJSON();

    const polygonAoi = {
      type: "FeatureCollection",
      features: [geojson],
    };

    onChange(polygonAoi);
  }


  function handleDeleted() {
    onChange(null);
  }


  return (
    <div className="area-selector">

      <div className="area-selector-header">

        <div>
          <h3>
            Select area to analyze
          </h3>

          <p>
            Draw a polygon on the map around
            the area you want TreeROI to analyze.
          </p>
        </div>

        {value && (
          <span className="area-selected">
            Area selected
          </span>
        )}

      </div>


      <MapContainer
        center={defaultCenter}
        zoom={14}
        className="selection-map"
        scrollWheelZoom={true}
      >

        <MapResizeHandler />

        <TileLayer
          attribution="© OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />


        <FeatureGroup>

          <EditControl
            position="topright"

            onCreated={handleCreated}
            onDeleted={handleDeleted}

            disabled={disabled}

            draw={{
              rectangle: false,
              circle: false,
              circlemarker: false,
              marker: false,
              polyline: false,

              polygon: {
                allowIntersection: false,

                /*
                 * Do not enable showArea here.
                 *
                 * react-leaflet-draw currently throws:
                 * "ReferenceError: type is not defined"
                 * from its area-measurement code.
                 */
                showArea: false,
              },
            }}

            edit={{
              edit: false,
              remove: true,
            }}
          />

        </FeatureGroup>

      </MapContainer>


      {!value && (
        <div className="area-selector-hint">
          Use the polygon tool in the upper-right
          corner of the map to outline your area.
        </div>
      )}

      {value && (
        <div className="area-selector-hint">
          Area selected. You can remove it and
          draw a new polygon if needed.
        </div>
      )}

    </div>
  );
}


export default AreaSelector;
