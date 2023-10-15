import React, { useState, useEffect } from "react";
import PropTypes, { array } from "prop-types";
import Post from "./post";

export default function Feed({ url }){
    const [postArr, setPostArr] = useState([]);
    useEffect(() => {
        let ignoreStaleRequest = false;
        
        //Call Rest API to get the list of posts on feed
        fetch(url, { credentials: "same-origin" })
            .then((response) => {
                if (!response.ok) throw Error(response.statusText);
                return response.json();
            })
            .then((data) => {
                if (!ignoreStaleRequest) {
                    let posts = []
                    setPostArr([...posts, ...data.results]);
                }
            })
            .catch((error) => console.log(error));

        return () => {
            // Cleanup function --> refer to post.jsx desc
            //    for more info about ignoreStaleRequest
            ignoreStaleRequest = true;
        }
    }, [url]);

    //define postFunc
    function postFunc(post){
        return <Post key={post.postid} url={`/api/v1/posts/${post.postid}/`}/>
    }

    // Render the feed
    return (
        <div id="feed">
            {console.log('rendering the feed!')}
            {postArr.map((post) => postFunc(post) )}
        </div>
        );
}

Feed.propTypes = {
    url: PropTypes.string.isRequired,
  };
