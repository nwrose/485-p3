import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { isConsoleMessageExcluded } from "cypress-fail-on-console-error";

dayjs.extend(relativeTime);
dayjs.extend(utc);

// owner, timestamp, ownerImgUrl are props for the infoBar component.
export default function InfoBar({ owner, timestamp, ownerImgUrl, postid }) {
  /* Display infoBar of a single post */

  // Render infoBar
  return (
    <div className="infoBar"> 
    {console.log('Rendering the infobar!')}
        <a href={`/users/${owner}/`}>
            <img src={ownerImgUrl} alt={`${owner}'s pfp`} className="pfp"/>
            &nbsp;{owner}0
        </a>
        <span>&nbsp;&nbsp;&nbsp;</span>
        <a href={`/posts/${postid}/`}>{timestamp}</a>
    </div>
  );
  //DONT FORGET TO MAKE TIMESTAMP HUMAN READABLE OR WAHTEVER
}

InfoBar.propTypes = {
  owner: PropTypes.string.isRequired,
  timestamp: PropTypes.string.isRequired,
  ownerImgUrl: PropTypes.string.isRequired,
  postid: PropTypes.number.isRequired,  
};