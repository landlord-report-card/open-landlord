import React from 'react';
import {
  MDBFooter,
  MDBContainer,
  MDBRow
} from 'mdb-react-ui-kit';


export default function Footer() {
  return (
    <>
    <MDBFooter bgColor='light' className='text-center text-lg-left'>

      <MDBContainer className='disclaimer-box'>
        <MDBRow>
            <p><br/>
                  All data is provided by the City of Albany, and any errors, omissions, and inaccuracies should be reported to the City of Albany. 
                  The Albany Landlord Report card is not affliated with or endorsed by the City of Albany.
                  This data is provided for informational purposes, as a public resource for general information.
                  You should not rely on this information for any business, legal, or other decision. 
                  The Albany Landlord Report Card is not responsible for and disclaims responsibility for any losses or damages, directly or otherwise, which may result from the use of this data. 
            </p>
        </MDBRow>
      </MDBContainer>

      <div className='text-center disclaimer-box' style={{ backgroundColor: 'rgba(0, 0, 0, 0.2)' }}>
        &copy; {new Date().getFullYear()} Copyright:{' '}
        <a className='text-dark' href='https://www.albanylandlord.com/'>
          Albany Landlord Report Card. 
        </a>
        &nbsp;All rights reserved.
      </div>
    </MDBFooter>
    </>
  );
}