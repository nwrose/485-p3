import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";git 
import Likes from "./likes"
import InfiniteScroll from 'react-infinite-scroll-component';

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [timestamp, setTimestamp] = useState("");
  const [postid, setPostid] = useState(-1);
  const [commentsInfo, setCommentInfo] = useState([]);
  const [numLikes, setNumLikes] = useState(-1);
  const [likeStatus, setLikeStatus] = useState(true);
  const [rmLikeUrl, setrmLikeUrl] = useState("");
  const [commentText, setCommentText] = useState("");
  const [trigger, setTrigger] = useState(false);
  const [loadingData, setLoadingData] = useState(true);

  //do the delete comment stuff
  function deleteComment(del_url){
    setLoadingData(true);
    console.log(`Deleting comment using api at: ${del_url}`);
    let delComment_ignoreStaleRequest = false;
    fetch(del_url, { credentials: "same-origin", method:'DELETE'})
        .then((response) => {
            if(!response.ok){
              throw Error(response.statusText);
            }
        })
        .then(() => {
            if(!delComment_ignoreStaleRequest){
              let val = !trigger;
              setTrigger(val);
            }
        })  
        .catch((error) => console.log(error));
        return () => {
            delComment_ignoreStaleRequest = true;
        }
  }


  //do the make comment stuff
  function makeComment(e){
    setLoadingData(true);
    console.log(`making comment:  ${commentText}`);
    e.preventDefault();
    fetch(`/api/v1/comments/?postid=${postid}`, {
        credentials: "same-origin", 
        method: "POST",
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({text: commentText})
    })
    .then((response) => {
        if(!response.ok) throw Error(response.statusText);
        setCommentText("")
        let val = !trigger;
        setTrigger(val);
        return response.json();
    })
    .catch((error) => console.log(error));
  }

  //Do the like button function stuff

  function doubleClick(){
    
    let double_ignoreStaleRequest = false;
    if(!likeStatus){
        setLoadingData(true);
        fetch(`/api/v1/likes/?postid=${postid}`, {credentials: "same-origin", method: "POST"})
        .then((response) => {
            if(!response.ok) throw Error(response.statusText);
            return response.json()
        })
        .then((data) => {
            if (!double_ignoreStaleRequest){
                let temp = numLikes + 1;
                setNumLikes(temp);
                let temp2 = data.url
                setrmLikeUrl(temp2);
                setLikeStatus(true);
            }
            let val = !trigger;
            setTrigger(val);
        })
        .catch((error) => console.log(error));
        return () => {
            double_ignoreStaleRequest = true;
        }}
  }

  function toggleLike() {
    setLoadingData(true);
    let like_ignoreStaleRequest = false;
    if (likeStatus){
        fetch(rmLikeUrl, { credentials: "same-origin", method:'DELETE'})
        .then((response) => {
            if(!response.ok) throw Error(response.statusText);
        })
        .then(() => {
            if(!like_ignoreStaleRequest){
                let temp = numLikes - 1;
                setNumLikes(temp);
                setrmLikeUrl("");
                setLikeStatus(false);
            }
            let val = !trigger;
            setTrigger(val);
        })  
        .catch((error) => console.log(error));
        return () => {
            like_ignoreStaleRequest = true;
        }
    }
    else{
        fetch(`/api/v1/likes/?postid=${postid}`, {credentials: "same-origin", method: "POST"})
        .then((response) => {
            if(!response.ok) throw Error(response.statusText);
            return response.json()
        })
        .then((data) => {
            if (!like_ignoreStaleRequest){
                let temp = numLikes + 1;
                setNumLikes(temp);
                let temp2 = data.url;
                setrmLikeUrl(temp2);
                setLikeStatus(true);
            }
            let val = !trigger;
            setTrigger(val);
        })
        .catch((error) => console.log(error));
        return () => {
            like_ignoreStaleRequest = true;
        }
    }
  }


  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setTimestamp(data.created);
          setOwnerImgUrl(data.ownerImgUrl);
          setPostid(data.postid);
          setCommentInfo(data.comments);
          setNumLikes(data.likes.numLikes);
          setLikeStatus(data.likes.lognameLikesThis);
          setrmLikeUrl(data.likes.url);
          setLoadingData(false);
        }
        
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [trigger]);

  // Render post image and post owner
  return (
    <div className="post">
      {loadingData ? <span>Loading Data...</span>: 
      <div>
      {console.log(`rendering post with postid: ${postid}`)}
      <div className="infoBar"> 
        <a href={`/users/${owner}/`}>
            <img src={ownerImgUrl} alt={`${owner}'s pfp`} className="pfp"/>
            &nbsp;{owner}
        </a>
        <span>&nbsp;&nbsp;&nbsp;</span>
        <a href={`/posts/${postid}/`}>{timestamp}</a>
      </div>

      <img src={imgUrl} alt="post_image" onDoubleClick={doubleClick}/>
      <Likes numLikes={numLikes} toggleLike={toggleLike} likeStatus={likeStatus}/>
      <div id="comments">
          {commentsInfo.map((comment) => (
            <p className="comment" key={comment.commentid}>
              <a href={comment.ownerShowUrl}>{comment.owner}</a>
              <span data-testid="comment-text">{comment.text}</span>
              {comment.lognameOwnsThis ? 
                <button
                  id={comment.commentid}
                  data-testid="delete-comment-button" 
                  onClick={(e) => deleteComment(comment.url)}>
                    Delete comment
                </button> : <span></span>
              }
            </p>
          ) )}
          <form onSubmit={makeComment} data-testid="comment-form">
              <input 
              name="newComment"
              type = "text"
              placeholder = "Make New Comment"
              value = {commentText}
              onChange={(e) => setCommentText(e.target.value)}
              />
          </form>
      </div>
      
      </div>
      }
    </div>
  );
}


Post.propTypes = {
  url: PropTypes.string.isRequired,
};  