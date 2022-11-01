import { useParams } from 'react-router-dom'

export default function Property () {
    let { id } = useParams();

    return (
        <div>
            <div className="main">
              <div className="container font-typewriter">
                <div className="row">
                  <div className="col-sm">
                    <div className="card" id="property-card">
                      <div className="card-body">
                        <div className="row title-row text-center">
                          <div className="col-sm">
                            <span className="property-label">Property Address</span>
                            <span className="property-address font-handwritten">property.address</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
        </div>
    );
}


