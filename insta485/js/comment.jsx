import React, { useState, useEffect } from "react";
import PropTypes, { object } from "prop-types";

// owner, timestamp, ownerImgUrl are props for the infoBar component.
export default function Comment({ commentInfo, deleteComment }) {
  /* Display a single comment */

  // Render comment
  return (
    <p className="comment">
        {console.log('rendering a single commment!')}
        <a href={commentInfo.ownerShowUrl}>{commentInfo.owner}</a>
        <span>{commentInfo.text}</span>
        {commentInfo.lognameOwnsThis ? 
        <button 
        data-testid="delete-comment-button" 
        onClick={deleteComment(commentInfo.url)}>
          Delete comment
        </button> : <span></span>}
    </p>
  );
}

Comment.propTypes = {
  commentInfo: PropTypes.object.isRequired,
  deleteComment: PropTypes.func.isRequired,
};