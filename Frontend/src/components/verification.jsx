import React, { useState } from 'react';
import {confirmCode} from '../helpers/authHelpers';
import { useNavigate } from 'react-router-dom';


export default function VerificationInput({email, setshowVerification}) {
    const [inputValue, setInputValue] = useState('');
    const navigate = useNavigate();


  const handleSubmit = async () => {
    if (inputValue.trim() === '') return;

    const data = {
        "email" : email,
        "code" : parseInt(inputValue)
    }

    const confirm_result = await confirmCode(data); // Check with server

    if (confirm_result) {
        setshowVerification(false);
        navigate("/login", { replace: true });
    }

    else{
        alert('Incorrect verfication code');
    }
  };

  const handleCancel = () => {
    setshowVerification(false);
  };



  return (

    <>

        <style>
        {`
        .verification-container {
            box-sizing: border-box;
            padding: 16px;
            background-color: #fff;
            border: 1px solid #ccc;
            width: 100%;
            margin-bottom: 16px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .verification-message {
            color: #374151;
            font-size: 0.875rem;
            margin: 0 0 12px 0;
        }

        .verification-input {
            box-sizing: border-box;
            width: 100%;
            padding: 8px;
            margin-bottom: 12px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        .verification-buttons {
            display: flex;
            justify-content: space-between;
        }

        .verification-cancel,
        .verification-submit {
            padding: 8px 12px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .verification-cancel {
            background-color: #ddd;
        }

        .verification-submit {
            background-color: #4caf50;
            color: white;
        }
        `}
    </style>
        <div className="verification-container">
        <p className="verification-message">
            Enter the verification code sent to {email}.
        </p>
        <input
            type="text"
            className="verification-input"
            placeholder="Enter verification code"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
        />
        <div className="verification-buttons">
            <button
            onClick={handleCancel}
            className="verification-cancel"
            >
            Cancel
            </button>
            <button
            onClick={handleSubmit}
            className="verification-submit"
            >
            Submit
            </button>
        </div>
        </div>

    </>
  );
}
