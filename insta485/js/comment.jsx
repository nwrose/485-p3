import React, { useState, useEffect } from "react";
import PropTypes, { object } from "prop-types";

// owner, timestamp, ownerImgUrl are props for the infoBar component.
export default function Comment({ commentInfo }) {
  /* Display a single comment */

  // Render comment
  return (
    <p className="comment">
        {console.log('rendering a single commment!')}
        <a href={commentInfo.ownerShowUrl}>{commentInfo.owner}</a>
        <span>{commentInfo.text}</span>
    </p>
  );
}

Comment.propTypes = {
  commentInfo: PropTypes.object.isRequired,
  makeComment: PropTypes.func.isRequired,
};