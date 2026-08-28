import { useState } from "react";

import AreaSelector from "./AreaSelector";


function SearchBox({
  onAnalyze,
  loading,
}) {
  const [date, setDate] =
    useState("2025-08-19");

  const [time, setTime] =
    useState("14:00");

  const [granularity, setGranularity] =
    useState(100);

  const [topN, setTopN] =
    useState(5);

  const [polygonAoi, setPolygonAoi] =
    useState(null);


  function handleSubmit(event) {
    event.preventDefault();

    if (!polygonAoi) {
      alert(
        "Please draw a polygon on the map first."
      );

      return;
    }

    const parameters = {
  polygonAoi,
  date,
  time,
  granularity: Number(granularity),
  topN: Number(topN),
};

  console.log(
  "========== TREEROI FRONTEND REQUEST =========="
);

console.log(
  JSON.stringify(parameters, null, 2)
);

console.log(
  "==============================================="
);

    onAnalyze(parameters);
  }

  return (
    <form
      className="search-box"
      onSubmit={handleSubmit}
    >

      <AreaSelector
        value={polygonAoi}
        onChange={setPolygonAoi}
        disabled={loading}
      />


      <div className="form-row">

        <div className="form-group">

          <label>
            Date
          </label>

          <input
            type="date"
            value={date}
            onChange={(event) =>
              setDate(event.target.value)
            }
            disabled={loading}
          />

        </div>


        <div className="form-group">

          <label>
            Time
          </label>

          <input
            type="time"
            value={time}
            onChange={(event) =>
              setTime(event.target.value)
            }
            disabled={loading}
          />

        </div>


        <div className="form-group">

          <label>
            Granularity
          </label>

          <input
            type="number"
            min="60"
            max="100"
            value={granularity}
            onChange={(event) =>
              setGranularity(event.target.value)
            }
            disabled={loading}
          />

        </div>


        <div className="form-group">

          <label>
            Top tiles
          </label>

          <select
            value={topN}
            onChange={(event) =>
              setTopN(event.target.value)
            }
            disabled={loading}
          >

            <option value={1}>
              1
            </option>

            <option value={2}>
              2
            </option>

            <option value={3}>
              3
            </option>

            <option value={4}>
              4
            </option>

            <option value={5}>
              5
            </option>

          </select>

        </div>

      </div>


      <button
        type="submit"
        disabled={loading}
      >
        {loading
          ? "Analyzing..."
          : "Analyze Area"}
      </button>

    </form>
  );
}


export default SearchBox;
